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
