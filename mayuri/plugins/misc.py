import re
import sys
from datetime import datetime
from mayuri import HELP_COMMANDS, OWNER, PREFIX
from mayuri.mayuri import Mayuri
from mayuri.utils.filters import sudo_only
from mayuri.utils.lang import tl
from mayuri.utils.misc import paginate_plugins
from pyrogram import enums, filters, __version__
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from re import IGNORECASE, I, match, sub
from sre_constants import error as sre_err

DELIMITERS = ("/", ":", "|", "_")

@Mayuri.on_message(filters.command("alive", PREFIX) | filters.command("on", PREFIX) & sudo_only)
async def alive(c, m):
	alive_text = "Bot services is running...\n"
	alive_text += "•  ⚙️ Pyrogram    : v{}\n".format(__version__)
	alive_text += "•  🐍 Python         : v{}".format(sys.version.split(' ')[0])
	start = datetime.now()
	msg = await m.reply_text(alive_text+"\n•  📶 Latency        : ⏳")
	end = datetime.now()
	latency = (end - start).microseconds / 1000
	text = alive_text+"\n•  📶 Latency        : {}ms".format(latency)
	await msg.edit(text)

@Mayuri.on_message(filters.command("start", PREFIX))
async def start_msg(c, m):
	chat_id = m.chat.id
	if m.chat.type != enums.ChatType.PRIVATE:
		return await m.reply_text(await tl(chat_id, "pm_me"))
	keyboard = None
	text = "hello!\n"
	text += "This bot is under development."
	text += "\nYou can contact my master [here](tg://user?id={})\n\n".format(OWNER)
	text += "Powered by [Pyrogram v{}](https://pyrogram.org)".format(__version__)
	await m.reply_text(text,reply_markup=keyboard)

async def help_parser(c, chat_id, text, keyboard=None):
	if not keyboard:
		keyboard = InlineKeyboardMarkup(await paginate_plugins(0, HELP_COMMANDS, "help", chat_id))
	await c.send_message(chat_id, text, parse_mode=enums.ParseMode.MARKDOWN, reply_markup=keyboard)

@Mayuri.on_message(filters.command("help", PREFIX))
async def help_msg(c, m):
	chat_id = m.chat.id
	if m.chat.type != enums.ChatType.PRIVATE:
		keyboard = InlineKeyboardMarkup(
			[[InlineKeyboardButton(text=await tl(chat_id, "helps"), url=f"t.me/{(await c.get_me()).username}?start=help")]])
		await m.reply(await tl(chat_id, "pm_me"), reply_markup=keyboard)
		return
	await help_parser(c, m.chat.id, (await tl(chat_id, "HELP_STRINGS")).format(", ".join(PREFIX)))

async def help_button_callback(_, __, query):
	if re.match(r"help_", query.data):
		return True

help_button_create = filters.create(help_button_callback)

@Mayuri.on_callback_query(help_button_create)
async def help_button(c, q):
	chat_id = q.message.chat.id
	mod_match = re.match(r"help_plugin\((.+?)\)", q.data)
	back_match = re.match(r"help_back", q.data)
	if mod_match:
		plugin = mod_match.group(1)
		text = (await tl(chat_id, "this_plugin_help")).format(await tl(chat_id, HELP_COMMANDS[plugin].__PLUGIN__)) \
			   + await tl(chat_id, HELP_COMMANDS[plugin].__HELP__)

		await q.message.edit(text=text,
			parse_mode=enums.ParseMode.MARKDOWN,
			reply_markup=InlineKeyboardMarkup(
				[[InlineKeyboardButton(text=await tl(chat_id, "back"), callback_data="help_back")]]))

	elif back_match:
		await q.message.edit(text=(await tl(chat_id, "HELP_STRINGS")).format(", ".join(PREFIX)),
			reply_markup=InlineKeyboardMarkup(await paginate_plugins(0, HELP_COMMANDS, "help", chat_id)))

def separate_sed(sed_string):
	if (
		len(sed_string) > 2
		and sed_string[1] in DELIMITERS
		and sed_string.count(sed_string[1]) >= 2
	):
		delim = sed_string[1]
		start = counter = 2
		while counter < len(sed_string):
			if sed_string[counter] == '\\':
				counter += 1

			elif sed_string[counter] == delim:
				replace = sed_string[start:counter]
				counter += 1
				start = counter
				break

			counter += 1

		else:
			return None

		while counter < len(sed_string):
			if (
				sed_string[counter] == '\\'
				and counter + 1 < len(sed_string)
				and sed_string[counter + 1] == delim
			):
				sed_string = sed_string[:counter] + sed_string[counter + 1 :]

			elif sed_string[counter] == delim:
				replace_with = sed_string[start:counter]
				counter += 1
				break

			counter += 1
		else:
			return replace, sed_string[start:], ''

		flags = ''
		if counter < len(sed_string):
			flags = sed_string[counter:]
		return replace, replace_with, flags.lower()
	return None

@Mayuri.on_message(filters.reply & filters.regex('^s/(.*?)'), group=101)
async def sed(c,m):
	"""For sed command, use sed on Telegram."""
	sed_result = separate_sed(m.text or m.caption)
	textx = m.reply_to_message
	if sed_result:
		if textx:
			to_fix = textx.text
		else:
			return await m.reply_text(
				"`Master, I don't have brains. Well you too don't I guess.`"
			)

		repl, repl_with, flags = sed_result

		if not repl:
			return await m.reply_text(
				"`Master, I don't have brains. Well you too don't I guess.`"
			)

		try:
			check = match(repl, to_fix, flags=IGNORECASE)
			if check and check.group(0).lower() == to_fix.lower():
				return await m.reply_text("`Boi!, that's a reply. Don't use sed`")

			if "i" in flags and "g" in flags:
				text = sub(repl, repl_with, to_fix, flags=I).strip()
			elif "i" in flags:
				text = sub(repl, repl_with, to_fix, count=1, flags=I).strip()
			elif "g" in flags:
				text = sub(repl, repl_with, to_fix).strip()
			else:
				text = sub(repl, repl_with, to_fix, count=1).strip()
		except sre_err:
			return await m.reply_text("B O I! [Learn Regex](https://regexone.com)")
		if text:
			await m.reply_text(text)
