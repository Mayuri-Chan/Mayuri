import cv2
import os
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
from random import random, choice, randint, shuffle

@Mayuri.on_message(filters.command("setwelcome", PREFIX) & admin_only)
async def set_welcome(c,m):
	db = c.db["welcome_settings"]
	chat_id = m.chat.id
	thread_id = 1
	enable = True
	clean_service = False
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
		if m.chat.is_forum:
			if (check and check['thread_id'] == 1):
				thread_id = m.message_thread_id
			elif not m.message_thread_id:
				thread_id = 1
	await db.update_one({'chat_id': chat_id}, {"$set": {'text': text, 'thread_id': thread_id, 'enable': enable, 'clean_service': clean_service}}, upsert=True)
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
	welc_settings = (await c.tl(chat_id, "welcome_settings")).format(check['enable'], check['clean_service'], check['thread_id'])
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
	await welcome_msg(c,m,True)

@Mayuri.on_chat_join_request()
async def join_request_handler(c,m):
	await welcome_msg(c,m,False)

async def welcome_msg(c,m,is_request):
	db = c.db["welcome_settings"]
	chat_id = m.chat.id
	if is_request:
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
		if not is_request or m.chat.is_forum:
			if m.chat.is_forum:
				if check['thread_id'] == 1:
					return
				wc_msg = await c.send_message(chat_id=chat_id, text=welcome_text, message_thread_id=check['thread_id'], reply_markup=button)
			else:
				wc_msg = await c.send_message(chat_id=chat_id, text=welcome_text, reply_markup=button)
		else:
			wc_msg = await m.reply_text(welcome_text, reply_markup=button)
