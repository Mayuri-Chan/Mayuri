import asyncio
import importlib
import os
import re
import sys
from datetime import datetime
from mayuri import HELP_COMMANDS, PREFIX
from mayuri.lang import list_all_lang
from mayuri.mayuri import Mayuri
from mayuri.plugins.captcha import gen_captcha
from mayuri.util.filters import sudo_only
from mayuri.util.misc import paginate_plugins
from mayuri.util.string import split_quotes
from pyrogram import enums, filters, __version__
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Mayuri.on_message(filters.command("alive", PREFIX) | filters.command("on", PREFIX) & sudo_only)
async def alive(c, m):
	alive_text = "Bot services is running...\n"
	alive_text += "•  ⚙️ PyroFork    : v{}\n".format(__version__)
	alive_text += "•  🐍 Python         : v{}".format(sys.version.split(' ')[0])
	start = datetime.now()
	msg = await m.reply_text(alive_text+"\n•  📶 Latency        : ⏳")
	end = datetime.now()
	latency = (end - start).microseconds / 1000
	text = alive_text+"\n•  📶 Latency        : {}ms".format(latency)
	await msg.edit(text)

async def create_captcha(c, m, db, verify_id, user_id):
	answer, file_name, buttons = await gen_captcha(verify_id,user_id)
	buttons.append([InlineKeyboardButton("🔄", callback_data=f"_captcha_regen_{verify_id}")])
	await db.update_one({'verify_id': verify_id}, {"$set": {'answer': answer}})
	return await m.reply_photo(photo=file_name, caption=(await c.tl(user_id, 'select_all_emojis')), reply_markup=InlineKeyboardMarkup(buttons))

@Mayuri.on_message(filters.command("start", PREFIX))
async def start_msg(c, m):
	db = c.db['captcha_list']
	chat_id = m.chat.id
	user_id = m.from_user.id
	if m.chat.type == enums.ChatType.CHANNEL:
		return await m.edit_text("chat_id: `{}`".format(m.chat.id))
	if m.chat.type != enums.ChatType.PRIVATE:
		return await m.reply_text(await c.tl(chat_id, "pm_me"))
	t = m.text.split()
	if len(t) > 1:
		if re.match(r"verify_.*", t[1]):
			r = re.search("(verify_)([a-zA-Z0-9]{1,})",t[1])
			verify_id = r.group(2)
			data = await db.find_one({'verify_id': verify_id})
			if data:
				if data['user_id'] != user_id:
					return await m.reply_text(await c.tl(chat_id, 'not_your_captcha'))
				msg = await m.reply_text(await c.tl(chat_id, 'generate_captcha'))
				await c.loop.create_task(create_captcha(c, m, db, verify_id, user_id))
				return await msg.delete()
			return await m.reply_text(await c.tl(chat_id, 'verify_id_not_found'))
	keyboard = None
	text = "hello!\n"
	text += "This bot is under development."
	text += "\nYou can contact my master [here](tg://user?id={})\n\n".format(c.config['bot']['OWNER'])
	text += "Powered by [Pyrofork v{}](https://pyrofork.mayuri.my.id)".format(__version__)
	await m.reply_text(text,reply_markup=keyboard)

async def help_parser(c, chat_id, text, keyboard=None):
	if not keyboard:
		keyboard = InlineKeyboardMarkup(await paginate_plugins(c, 0, HELP_COMMANDS, "help", chat_id))
	await c.send_message(chat_id, text, parse_mode=enums.ParseMode.MARKDOWN, reply_markup=keyboard)

@Mayuri.on_message(filters.command("help", PREFIX))
async def help_msg(c, m):
	chat_id = m.chat.id
	if m.chat.type != enums.ChatType.PRIVATE:
		keyboard = InlineKeyboardMarkup(
			[[InlineKeyboardButton(text=await c.tl(chat_id, "helps"), url=f"t.me/{(await c.get_me()).username}?start=help")]])
		await m.reply(await c.tl(chat_id, "pm_me"), reply_markup=keyboard)
		return
	await help_parser(c, m.chat.id, (await c.tl(chat_id, "HELP_STRINGS")).format(", ".join(PREFIX)))

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
		text = (await c.tl(chat_id, "this_plugin_help")).format(await c.tl(chat_id, HELP_COMMANDS[plugin].__PLUGIN__)) \
			   + await c.tl(chat_id, HELP_COMMANDS[plugin].__HELP__)

		await q.message.edit(text=text,
			parse_mode=enums.ParseMode.MARKDOWN,
			reply_markup=InlineKeyboardMarkup(
				[[InlineKeyboardButton(text=await c.tl(chat_id, "back"), callback_data="help_back")]]))

	elif back_match:
		await q.message.edit(text=(await c.tl(chat_id, "HELP_STRINGS")).format(", ".join(PREFIX)),
			reply_markup=InlineKeyboardMarkup(await paginate_plugins(c, 0, HELP_COMMANDS, "help", chat_id)))

@Mayuri.on_message(filters.command("info", PREFIX))
async def user_info(c,m):
	chat_id = m.chat.id
	text = m.text
	text = text.split(None, 1)
	msg = await m.reply_text(await c.tl(chat_id, "geting_info"))
	if m.reply_to_message:
		if m.reply_to_message.sender_chat:
			return msg.edit_text(await c.tl(chat_id, "infouser_is_channel"))
		user_id = m.reply_to_message.from_user.id
	else:
		if len(text) > 1:
			extracted = split_quotes(text[1])
			if re.match(r"([0-9]{1,})", text[1].lower()):
				user_id = text[1]
			elif len(extracted) > 1:
				user_id = extracted[0]
			else:
				user_id = text[1]
		else:
			if m.sender_chat:
				return await msg.edit_text(await c.tl(chat_id, "need_user_id"))
			user_id = m.from_user.id
	try:
		user = await c.get_users(user_id)
	except FloodWait as e:
		await asyncio.sleep(e.value)
	except RPCError:
		return await msg.edit_text(await c.tl(chat_id, "need_user_id"))
	text = await c.tl(chat_id, "infouser_info")
	text += (await c.tl(chat_id, "infouser_id")).format(user.id)
	text += (await c.tl(chat_id, "infouser_firstname")).format(user.first_name)
	text += (await c.tl(chat_id, "infouser_lastname")).format(user.last_name)
	text += (await c.tl(chat_id, "infouser_name")).format(user.username)
	text += (await c.tl(chat_id, "infouser_link")).format(user.id)
	if user.photo:
		target = "images/users/"+user.photo.big_file_id+".png"
		await c.download_media(user.photo.big_file_id, file_name=target)
		await msg.delete()
		target = "mayuri/"+target
		await m.reply_photo(photo=open(target, 'rb'), caption=text)
		return os.remove(target)
	await msg.edit_text(text)

@Mayuri.on_message(filters.command("setlang", PREFIX) | filters.command("lang", PREFIX))
async def set_language(c,m):
	db = c.db["chat_settings"]
	chat_id = m.chat.id
	#text = m.text.split(None, 1)
	if m.chat.type != enums.ChatType.PRIVATE and not await c.check_admin(chat_id,m.from_user.id):
		return
	#if len(text) > 1:
	#	lang = text[1]
	buttons = []
	temp = []
	check = await db.find_one({'chat_id': chat_id})
	if check and "lang" in check:
		curr_lang = check["lang"]
	else:
		curr_lang = 'id'
	i = 1
	for lang in list_all_lang():
		t = importlib.import_module("mayuri.lang."+lang)
		data = "setlang_{}".format(lang)
		if lang == curr_lang:
			text = f"* {t.lang_name}"
		else:
			text = t.lang_name
		temp.append(InlineKeyboardButton(text=text, callback_data=data))
		if i % 2 == 0:
			buttons.append(temp)
			temp = []
		if i == len(list_all_lang()):
			buttons.append(temp)
		i += 1
	await m.reply_text(text=(await c.tl(chat_id, "select_lang")), reply_markup=InlineKeyboardMarkup(buttons))

async def set_lang_callback(_, __, query):
	if re.match(r"setlang_", query.data):
		return True

set_lang_create = filters.create(set_lang_callback)

@Mayuri.on_callback_query(set_lang_create)
async def set_lang_respond(c,q):
	db = c.db["chat_settings"]
	m = q.message
	if m.chat.type != enums.ChatType.PRIVATE and not await c.check_admin(m.chat.id,q.from_user.id):
		return await c.answer_callback_query(callback_query_id=q.id, text="You're not admin!", show_alert=True)
	lang = q.data[8:]
	await db.update_one({'chat_id': m.chat.id},{"$set": {'lang': lang}}, upsert=True)
	await m.edit(text=await c.tl(m.chat.id, "language_changed"))
