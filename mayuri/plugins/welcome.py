import cv2
import os
import random
import re
import string
import time
from mayuri import PREFIX
from mayuri.mayuri import Mayuri
from mayuri.util.filters import admin_only, sudo_only
from mayuri.util.string import parse_button, build_keyboard
from pyrogram import enums, filters
from pyrogram.errors import RPCError
from pyrogram.types import InputMediaPhoto
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup

@Mayuri.on_message(filters.command("setwelcome", PREFIX) & admin_only)
async def set_welcome(c,m):
	db = c.db["welcome_settings"]
	chat_id = m.chat.id
	thread_id = 1
	enable = True
	clean_service = False
	is_captcha = False
	verify_text = None
	if m.reply_to_message:
		text = m.reply_to_message.text
	else:
		text = text.split(None,1)
		text = text[1]
	check = await db.find_one({'chat_id': chat_id})
	if check:
		enable = check['enable']
		clean_service = check['clean_service']
		thread_id = check['thread_id']
		is_captcha = check['is_captcha']
		verify_text = check['verify_text']
		if m.chat.is_forum:
			if (check and check['thread_id'] == 1):
				thread_id = m.message_thread_id
			elif not m.message_thread_id:
				thread_id = 1
	await db.update_one({'chat_id': chat_id}, {"$set": {'text': text, 'thread_id': thread_id, 'enable': enable, 'clean_service': clean_service, 'is_captcha': is_captcha, 'verify_text': verify_text}}, upsert=True)
	r_text = await c.tl(chat_id, "welcome_set")
	await m.reply_text(r_text)

@Mayuri.on_message(filters.command("setwelcomethread", PREFIX) & admin_only)
async def set_thread(c,m):
	db = c.db["welcome_settings"]
	chat_id = m.chat.id
	if not m.chat.is_forum:
		return await m.reply_text(await c.tl(chat_id, "not_forum"))
	check = await db.find_one({'chat_id': chat_id})
	if not check:
		return await m.reply_text(await c.tl(chat_id, "welcome_not_set"))
	if m.message_thread_id:
		thread_id = m.message_thread_id
	else:
		thread_id = 1
	await db.update_one({'chat_id': chat_id}, {"$set": {'thread_id': thread_id}})
	await m.reply_text(await c.tl(chat_id, "thread_id_set"))

@Mayuri.on_message(filters.command("welcome", PREFIX) & admin_only)
async def welcome(c,m):
	db = c.db["welcome_settings"]
	chat_id = m.chat.id
	text = m.text
	text = text.split(None, 1)
	check = await db.find_one({'chat_id': chat_id})
	if not check:
		return await m.reply_text(await c.tl(chat_id, "welcome_not_set"))
	welc_settings = (await c.tl(chat_id, "welcome_settings")).format(check['enable'], check['clean_service'], check['thread_id'], check['is_captcha'], check['verify_text'])
	if len(text) < 2:
		if not check['text']:
			text = await c.tl(chat_id, "default-welcome")
		else:
			text = check['text']
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
		if m.chat.is_forum and check['thread_id'] == 1:
			thread_id = m.message_thread_id
		else:
			thread_id = check['thread_id']
		await db.update_one({'chat_id': chat_id}, {"$set": {'enable': True}})
		return await m.reply_text(await c.tl(chat_id, "welcome_enabled"))
	if args in ['off', 'no']:
		await db.update_one({'chat_id': chat_id}, {"$set": {'enable': False}})
		return await m.reply_text(await c.tl(chat_id, "welcome_disabled"))
	if args == "noformat":
		await m.reply_text(welc_settings)
		return await m.reply_text(check['text'], parse_mode=enums.ParseMode.DISABLED)

@Mayuri.on_message(filters.group, group=10)
async def welcome_handler(c,m):
	await welcome_msg(c,m,False)

@Mayuri.on_chat_join_request()
async def join_request_handler(c,m):
	await welcome_msg(c,m,True)

async def welcome_msg(c,m,is_request):
	db = c.db["welcome_settings"]
	chat_id = m.chat.id
	if not is_request:
		new_members = m.new_chat_members
		if not new_members:
			return
	else:
		new_members = [m.from_user]
	check = await db.find_one({'chat_id': chat_id})
	if not check or (check and not check['enable']):
		return
	if check['clean_service']:
		await m.delete()
	for new_member in new_members:
		if not check['text']:
			text = await c.tl(chat_id, "default-welcome")
		else:
			text = check['text']
		text, button = parse_button(text)
		button = build_keyboard(button)
		if check['is_captcha']:
			await c.restrict_chat_member(chat_id, new_member.id, ChatPermissions())
			if check['verify_text']:
				verify_text = check['verify_text']
			else:
				verify_text = await c.tl(chat_id, 'verif_text')
			verify_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(10))
			if button:
				button.append([InlineKeyboardButton(verify_text, url=f"https://t.me/{c.me.username}?start=verify_{verify_id}")])
			else:
				button = [[InlineKeyboardButton(verify_text, url=f"https://t.me/{c.me.username}?start=verify_{verify_id}")]]
		if button:
			button = InlineKeyboardMarkup(button)
		else:
			button = None
		username = new_member.username
		if username:
			username = "@{}".format(username)
		welcome_text = (text).format(
			chatname=m.chat.title,
			first=new_member.first_name,
			last=new_member.last_name,
			fullname="{} {}".format(new_member.first_name, new_member.last_name),
			id=new_member.id,
			username=username,
			mention=new_member.mention
		)
		if is_request and m.chat.type == enums.ChatType.PRIVATE and check['is_captcha']:
			await c.send_message(new_member.id, text=welcome_text, reply_markup=button)
		if m.chat.is_forum:
			try:
				wc_msg = await c.send_message(chat_id=chat_id, text=welcome_text, message_thread_id=check['thread_id'], reply_markup=button)
			except Exception:
				pass
		else:
			wc_msg = await m.reply_text(welcome_text, reply_markup=button)
		if check['is_captcha']:
			captcha_db = c.db['captcha_list']
			await captcha_db.insert_one({'verify_id': verify_id, 'chat_id': chat_id, 'user_id': new_member.id, 'answer': [], 'right': 0, 'wrong': 0, 'msg_id': wc_msg.id})

@Mayuri.on_message(filters.group & filters.command("welcomecaptcha", PREFIX) & admin_only)
async def set_captcha(c,m):
	db = c.db["welcome_settings"]
	chat_id = m.chat.id
	text = m.text
	text = text.split(None, 1)
	if len(text) < 2:
		return
	check = await db.find_one({'chat_id': chat_id})
	if not check:
		return await m.reply_text(await c.tl(chat_id, "welcome_not_set"))
	args = text[1]
	if args in ['on', 'yes']:
		await db.update_one({'chat_id': chat_id},{"$set": {'is_captcha': True}})
		return await m.reply_text(await c.tl(chat_id, "captcha_enabled"))
	if args in ['off', 'no']:
		await db.update_one({'chat_id': chat_id},{"$set": {'is_captcha': False}})
		return await m.reply_text(await c.tl(chat_id, "captcha_disabled"))
