from mayuri import PREFIX
from mayuri.db import welcome as sql
from mayuri.mayuri import Mayuri
from mayuri.utils.filters import admin_only
from mayuri.utils.lang import tl
from mayuri.utils.string import parse_button, build_keyboard
from pyrogram import enums, filters
from pyrogram.types import InlineKeyboardMarkup

@Mayuri.on_message(filters.command("setwelcome", PREFIX) & admin_only)
async def set_welcome(c,m):
	chat_id = m.chat.id
	thread_id = 0
	enable = True
	clean_service = False
	if m.reply_to_message:
		text = m.reply_to_message.text
	else:
		args = m.text
		text = text.split(None,1)
		text = text[1]
	check = sql.get_welcome(chat_id)
	if check:
		if not check.enable:
			enable = False
		if check.clean_service:
			clean_service = True
		if check.thread_id != 0:
			thread_id = check.thread_id
	if m.chat.is_forum and check.thread_id == 0:
		thread_id = m.message_thread_id
	sql.set_welcome(chat_id, text, thread_id, enable, clean_service)
	r_text = await tl(chat_id, "welcome_set")
	await m.reply_text(r_text)

@Mayuri.on_message(filters.command("setwelcomethread", PREFIX) & admin_only)
async def set_thread(c,m):
	chat_id = m.chat.id
	if not m.chat.is_forum:
		return await m.reply_text(await tl(chat_id, "not_forum"))
	check = sql.get_welcome(chat_id)
	if not check:
		return await m.reply_text(await tl(chat_id, "welcome_not_set"))
	sql.set_welcome(chat_id, check.text, m.message_thread_id, check.enable, check.clean_service)
	await m.reply_text(await tl(chat_id, "thread_id_set"))

@Mayuri.on_message(filters.command("welcome", PREFIX) & admin_only)
async def welcome(c,m):
	chat_id = m.chat.id
	text = m.text
	text = text.split(None, 1)
	check = sql.get_welcome(chat_id)
	if not check:
		return await m.reply_text(await tl(chat_id, "welcome_not_set"))
	welc_settings = (await tl(chat_id, "welcome_settings")).format(check.enable, check.clean_service, check.thread_id)
	if len(text) < 2:
		if not check.text:
			text = await tl(chat_id, "default-welcome")
		else:
			text = check.text
		text, button = parse_button(text)
		button = build_keyboard(button)
		if button:
			button = InlineKeyboardMarkup(button)
		else:
			button = None
		await m.reply_text(welc_settings)
		return await m.reply_text(text, reply_markup=button)
	args = text[1]
	if args in ['on', 'yes']:
		if m.chat.is_forum and check.thread_id == 0:
			thread_id = m.message_thread_id
		else:
			thread_id = check.thread_id
		sql.set_welcome(check.chat_id, check.text, thread_id, True, check.clean_service)
		return await m.reply_text(await tl(chat_id, "welcome_enabled"))
	if args in ['off', 'no']:
		sql.set_welcome(check.chat_id, check.text, check.thread_id, False, check.clean_service)
		return await m.reply_text(await tl(chat_id, "welcome_disabled"))
	if args == "noformat":
		await m.reply_text(welc_settings)
		return await m.reply_text(check.text, parse_mode=enums.ParseMode.DISABLED)

@Mayuri.on_message(filters.group, group=10)
async def welcome_msg(c,m):
	chat_id = m.chat.id
	new_members = m.new_chat_members
	if not new_members:
		return
	check = sql.get_welcome(chat_id)
	if not check or (check and not check.enable):
		return
	if check.clean_service:
		await m.delete()
	for new_member in new_members:
		if not check.text:
			text = await tl(chat_id, "default-welcome")
		else:
			text = check.text
		text, button = parse_button(text)
		button = build_keyboard(button)
		if button:
			button = InlineKeyboardMarkup(button)
		else:
			button = None
		welcome_text = (text).format(
			chatname=m.chat.title,
			first=new_member.first_name,
			last=new_member.last_name,
			fullname="{} {}".format(new_member.first_name, new_member.last_name),
			id=new_member.id,
			username=new_member.username,
			mention=new_member.mention
		)
		if m.chat.is_forum:
			if check.thread_id == 0:
				return
			#return await c.send_message(chat_id=chat_id, text=welcome_text, message_thread_id=check.thread_id, reply_markup=button)
			return await c.send_message(chat_id=chat_id, text=welcome_text, reply_to_message_id=check.thread_id, reply_markup=button)
		await m.reply_text(welcome_text, reply_markup=button)
