import asyncio
import re
import time

from datetime import datetime
from mayuri import LOG_CHAT, OWNER, PREFIX
from mayuri.db import global_restrict as sql
from mayuri.mayuri import Mayuri
from mayuri.plugins.admin import check_admin
from mayuri.plugins.sudo import check_sudo
from mayuri.utils.filters import sudo_only
from mayuri.utils.lang import tl
from mayuri.utils.string import split_quotes
from mayuri.utils.time import create_time, time_left, tl_time
from pyrogram import enums, filters
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import ChatPermissions

#__PLUGIN__ = "blacklist"
#__HELP__ = "blacklist_help"

async def gban_task(c,m):
	chat_id = m.chat.id
	sudo_mention = m.from_user.mention
	text = m.text
	text = text.split(None, 1)
	duration = ""
	reason = ""
	until = 0
	msg = await m.reply_text("GBanning...")
	if m.reply_to_message:
		user = m.reply_to_message.from_user
		if len(text) > 1:
			extracted = split_quotes(text[1])
			if re.match(r"([0-9]{1,})([dhms])", text[1].lower()):
				duration = text[1].lower()
				if len(text) > 2:
					reason = text[2]
			elif re.match(r"([0-9]{1,})([dhms])", extracted[0].lower()):
				duration = extracted[0].lower()
				if len(extracted) > 1:
					reason = extracted[1]
			else:
				reason = text[1]
	else:
		if len(text) > 1:
			extracted = split_quotes(text[1])
			if re.match(r"([0-9]{1,})", text[1].lower()):
				user_id = text[1]
			elif len(extracted) > 1:
				if re.match(r"([0-9]{1,})([dhms])", extracted[1].lower()):
					duration = extracted[1].lower()
				extracted1 = split_quotes(extracted[1])
				if re.match(r"([0-9]{1,})([dhms])", extracted1[0].lower()):
					duration = extracted1[0].lower()
					if len(extracted1) > 1:
						reason = extracted1[1]
				else:
					reason = extracted[1]
				user_id = extracted[0]
			else:
				user_id = text[1]
		else:
			return await msg.edit_text(await tl(chat_id, "need_user_id"))
		try:
			user = await c.get_users(user_id)
		except FloodWait as e:
			await asyncio.sleep(e.value)
		except RPCError:
			return await msg.edit_text(await tl(chat_id, "need_user_id"))
	if user.id == int(OWNER):
		return await msg.edit_text(await tl(chat_id, "why_gban_owner"))
	if await check_sudo(user.id):
		return await msg.edit_text(await tl(chat_id, "why_gban_sudo"))
	if duration:
		until = create_time(duration)
	sql.add_to_gban(user.id,reason,until)
	for chat in sql.chat_list():
		if await check_admin(chat.chat_id,user.id):
			continue
		try:
			if duration:
				await c.ban_chat_member(chat.chat_id, user.id, datetime.fromtimestamp(until))
			else:
				await c.ban_chat_member(chat.chat_id, user.id)
		except RPCError:
			print(RPCError)
	text = (await tl(chat_id, "gbanned")).format(user.mention)
	log = await tl(chat_id, "new_gban")
	log += (await tl(chat_id, "infouser_sudo")).format(sudo_mention)
	log += (await tl(chat_id, "infouser_id")).format(user.id)
	log += (await tl(chat_id, "infouser_firstname")).format(user.first_name)
	log += (await tl(chat_id, "infouser_lastname")).format(user.last_name)
	log += (await tl(chat_id, "infouser_name")).format(user.username)
	log += (await tl(chat_id, "infouser_link")).format(user.id)
	if duration:
		log += (await tl(chat_id, "infouser_duration")).format(tl_time(duration))
		text += (await tl(chat_id, "blacklist_for")).format(tl_time(duration))
	if reason:
		log += (await tl(chat_id, "blacklist_reason"))
		text += (await tl(chat_id, "blacklist_reason"))
	await c.send_text(chat_id=LOG_CHAT, text=log)
	await msg.edit_text(text)

@Mayuri.on_message(filters.command("gban", PREFIX) & sudo_only)
async def gban(c,m):
	asyncio.create_task(gban_task(c,m))

async def gmute_task(c,m):
	chat_id = m.chat.id
	sudo_mention = m.from_user.mention
	text = m.text
	text = text.split(None, 1)
	duration = ""
	reason = ""
	until = 0
	msg = await m.reply_text("GMuting...")
	if m.reply_to_message:
		user = m.reply_to_message.from_user
		if len(text) > 1:
			extracted = split_quotes(text[1])
			if re.match(r"([0-9]{1,})([dhms])", text[1].lower()):
				duration = text[1].lower()
				if len(text) > 2:
					reason = text[2]
			elif re.match(r"([0-9]{1,})([dhms])", extracted[0].lower()):
				duration = extracted[0].lower()
				if len(extracted) > 1:
					reason = extracted[1]
			else:
				reason = text[1]
	else:
		if len(text) > 1:
			extracted = split_quotes(text[1])
			if re.match(r"([0-9]{1,})", text[1].lower()):
				user_id = text[1]
			elif len(extracted) > 1:
				if re.match(r"([0-9]{1,})([dhms])", extracted[1].lower()):
					duration = extracted[1].lower()
				extracted1 = split_quotes(extracted[1])
				if re.match(r"([0-9]{1,})([dhms])", extracted1[0].lower()):
					duration = extracted1[0].lower()
					if len(extracted1) > 1:
						reason = extracted1[1]
				else:
					reason = extracted[1]
				user_id = extracted[0]
			else:
				user_id = text[1]
		else:
			return await msg.edit_text(await tl(chat_id, "need_user_id"))
		try:
			user = await c.get_users(user_id)
		except FloodWait as e:
			await asyncio.sleep(e.value)
		except RPCError:
			return await msg.edit_text(await tl(chat_id, "need_user_id"))
	if user.id == int(OWNER):
		return await msg.edit_text(await tl(chat_id, "why_gmute_owner"))
	if await check_sudo(user.id):
		return await msg.edit_text(await tl(chat_id, "why_gmute_sudo"))
	if duration:
		until = create_time(duration)
	sql.add_to_gmute(user.id,reason,until)
	for chat in sql.chat_list():
		if await check_admin(chat.chat_id,user.id):
			continue
		try:
			if duration:
				await c.restrict_chat_member(chat.chat_id, user.id, ChatPermissions(), datetime.fromtimestamp(until))
			else:
				await c.restrict_chat_member(chat.chat_id, user.id, ChatPermissions())
		except RPCError:
			print(RPCError)
	text = (await tl(chat_id, "gmuted")).format(user.mention)
	log = await tl(chat_id, "new_gmute")
	log += (await tl(chat_id, "infouser_sudo")).format(sudo_mention)
	log += (await tl(chat_id, "infouser_id")).format(user.id)
	log += (await tl(chat_id, "infouser_firstname")).format(user.first_name)
	log += (await tl(chat_id, "infouser_lastname")).format(user.last_name)
	log += (await tl(chat_id, "infouser_name")).format(user.username)
	log += (await tl(chat_id, "infouser_link")).format(user.id)
	if duration:
		log += (await tl(chat_id, "infouser_duration")).format(tl_time(duration))
		text += (await tl(chat_id, "blacklist_for")).format(tl_time(duration))
	if reason:
		log += (await tl(chat_id, "blacklist_reason"))
		text += (await tl(chat_id, "blacklist_reason"))
	await c.send_text(chat_id=LOG_CHAT, text=log)
	await msg.edit_text(text)

@Mayuri.on_message(filters.command("gmute", PREFIX) & sudo_only)
async def gmute(c,m):
	asyncio.create_task(gmute_task(c,m))

@Mayuri.on_message(filters.command("gdmute", PREFIX) & sudo_only)
async def gdmute(c,m):
	chat_id = m.chat.id
	sudo_id = m.from_user.id
	sudo_mention = m.from_user.mention
	text = m.text
	text = text.split(None, 1)
	duration = ""
	reason = ""
	until = 0
	msg = await m.reply_text("GDMuting...")
	if m.reply_to_message:
		user = m.reply_to_message.from_user
		if len(text) > 1:
			extracted = split_quotes(text[1])
			if re.match(r"([0-9]{1,})([dhms])", text[1].lower()):
				duration = text[1].lower()
				if len(text) > 2:
					reason = text[2]
			elif re.match(r"([0-9]{1,})([dhms])", extracted[0].lower()):
				duration = extracted[0].lower()
				if len(extracted) > 1:
					reason = extracted[1]
			else:
				reason = text[1]
	else:
		if len(text) > 1:
			extracted = split_quotes(text[1])
			if re.match(r"([0-9]{1,})", text[1].lower()):
				user_id = text[1]
			elif len(extracted) > 1:
				if re.match(r"([0-9]{1,})([dhms])", extracted[1].lower()):
					duration = extracted[1].lower()
				extracted1 = split_quotes(extracted[1])
				if re.match(r"([0-9]{1,})([dhms])", extracted1[0].lower()):
					duration = extracted1[0].lower()
					if len(extracted1) > 1:
						reason = extracted1[1]
				else:
					reason = extracted[1]
				user_id = extracted[0]
			else:
				user_id = text[1]
		else:
			return await msg.edit_text(await tl(chat_id, "need_user_id"))
		try:
			user = await c.get_users(user_id)
		except FloodWait as e:
			await asyncio.sleep(e.value)
		except RPCError:
			return await msg.edit_text(await tl(chat_id, "need_user_id"))
	if user.id == int(OWNER):
		return await msg.edit_text(await tl(chat_id, "why_gdmute_owner"))
	if await check_sudo(user.id) and sudo_id != int(OWNER):
		return await msg.edit_text(await tl(chat_id, "why_gdmute_sudo"))
	if duration:
		until = create_time(duration)
	sql.add_to_gdmute(user.id,reason,until)
	text = (await tl(chat_id, "gdmuted")).format(user.mention)
	log = await tl(chat_id, "new_gdmute")
	log += (await tl(chat_id, "infouser_sudo")).format(sudo_mention)
	log += (await tl(chat_id, "infouser_id")).format(user.id)
	log += (await tl(chat_id, "infouser_firstname")).format(user.first_name)
	log += (await tl(chat_id, "infouser_lastname")).format(user.last_name)
	log += (await tl(chat_id, "infouser_name")).format(user.username)
	log += (await tl(chat_id, "infouser_link")).format(user.id)
	if duration:
		log += (await tl(chat_id, "infouser_duration")).format(tl_time(duration))
		text += (await tl(chat_id, "blacklist_for")).format(tl_time(duration))
	if reason:
		log += (await tl(chat_id, "blacklist_reason"))
		text += (await tl(chat_id, "blacklist_reason"))
	await c.send_text(chat_id=LOG_CHAT, text=log)
	await msg.edit_text(text)

async def ungban_task(c,m):
	chat_id = m.chat.id
	sudo_mention = m.from_user.mention
	text = m.text
	text = text.split(None, 1)
	msg = await m.reply_text("Ungbanning...")
	if m.reply_to_message:
		user = m.reply_to_message.from_user
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
			return await msg.edit_text(await tl(chat_id, "need_user_id"))
		try:
			user = await c.get_users(user_id)
		except FloodWait as e:
			await asyncio.sleep(e.value)
		except RPCError:
			return await msg.edit_text(await tl(chat_id, "need_user_id"))
	sql.rm_from_gban(user.id)
	for chat in sql.chat_list():
		if await check_admin(chat.chat_id,user.id):
			continue
		try:
			await c.unban_chat_member(chat.chat_id, user.id)
		except RPCError:
			print(RPCError)
	text = (await tl(chat_id, "ungbanned")).format(user.mention)
	log = await tl(chat_id, "new_ungban")
	log += (await tl(chat_id, "infouser_sudo")).format(sudo_mention)
	log += (await tl(chat_id, "infouser_id")).format(user.id)
	log += (await tl(chat_id, "infouser_firstname")).format(user.first_name)
	log += (await tl(chat_id, "infouser_lastname")).format(user.last_name)
	log += (await tl(chat_id, "infouser_name")).format(user.username)
	log += (await tl(chat_id, "infouser_link")).format(user.id)
	await c.send_text(chat_id=LOG_CHAT, text=log)
	await msg.edit_text(text)

@Mayuri.on_message(filters.command("ungban", PREFIX) & sudo_only)
async def ungban(c,m):
	asyncio.create_task(ungban_task(c,m))

async def ungmute_task(c,m):
	chat_id = m.chat.id
	sudo_mention = m.from_user.mention
	text = m.text
	text = text.split(None, 1)
	msg = await m.reply_text("Ungmuting...")
	if m.reply_to_message:
		user = m.reply_to_message.from_user
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
			return await msg.edit_text(await tl(chat_id, "need_user_id"))
		try:
			user = await c.get_users(user_id)
		except FloodWait as e:
			await asyncio.sleep(e.value)
		except RPCError:
			return await msg.edit_text(await tl(chat_id, "need_user_id"))
	sql.rm_from_gmute(user.id)
	for chat in sql.chat_list():
		if await check_admin(chat.chat_id,user.id):
			continue
		try:
			curr = (await c.get_chat(chat.chat_name)).permissions
			await c.restrict_chat_member(chat.chat_id,user.id, curr)
		except RPCError:
			print(RPCError)
	text = (await tl(chat_id, "ungmute")).format(user.mention)
	log = await tl(chat_id, "new_ungmute")
	log += (await tl(chat_id, "infouser_sudo")).format(sudo_mention)
	log += (await tl(chat_id, "infouser_id")).format(user.id)
	log += (await tl(chat_id, "infouser_firstname")).format(user.first_name)
	log += (await tl(chat_id, "infouser_lastname")).format(user.last_name)
	log += (await tl(chat_id, "infouser_name")).format(user.username)
	log += (await tl(chat_id, "infouser_link")).format(user.id)
	await c.send_text(chat_id=LOG_CHAT, text=log)
	await msg.edit_text(text)

@Mayuri.on_message(filters.command("ungmute", PREFIX) & sudo_only)
async def ungmute(c,m):
	asyncio.create_task(ungmute_task(c,m))

@Mayuri.on_message(filters.command("ungdmute", PREFIX) & sudo_only)
async def ungdmute(c,m):
	chat_id = m.chat.id
	sudo_id = m.from_user.id
	sudo_mention = m.from_user.mention
	text = m.text
	text = text.split(None, 1)
	msg = await m.reply_text("Ungdmuting...")
	if m.reply_to_message:
		user = m.reply_to_message.from_user
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
			return await msg.edit_text(await tl(chat_id, "need_user_id"))
		try:
			user = await c.get_users(user_id)
		except FloodWait as e:
			await asyncio.sleep(e.value)
		except RPCError:
			return await msg.edit_text(await tl(chat_id, "need_user_id"))
	if await check_sudo(user.id) and sudo_id != int(OWNER):
		return await msg.edit_text(await tl(chat_id, "why_ungdmute_sudo"))
	sql.rm_from_gdmute(user_id)
	text = (await tl(chat_id, "ungdmute")).format(user.mention)
	log = await tl(chat_id, "new_ungdmute")
	log += (await tl(chat_id, "infouser_sudo")).format(sudo_mention)
	log += (await tl(chat_id, "infouser_id")).format(user.id)
	log += (await tl(chat_id, "infouser_firstname")).format(user.first_name)
	log += (await tl(chat_id, "infouser_lastname")).format(user.last_name)
	log += (await tl(chat_id, "infouser_name")).format(user.username)
	log += (await tl(chat_id, "infouser_link")).format(user.id)
	await c.send_text(chat_id=LOG_CHAT, text=log)
	await msg.edit_text(text)

@Mayuri.on_message(filters.group, group=105)
async def gban_watcher(c,m):
	chat_id = m.chat.id
	user_id = m.from_user.id
	mention = m.from_user.mention
	now = time.time()
	if await check_admin(chat_id,user_id):
		return
	check = sql.check_gban(user_id)
	if not check:
		return
	until = check.until
	if until != 0:
		if until > now:
			if until-now < 40:
				until = now+40
			await c.ban_chat_member(chat_id, user_id, datetime.fromtimestamp(until))
		else:
			return sql.rm_from_gban(user_id)
	else:
		await c.ban_chat_member(chat_id, user_id)
	text = (await tl(chat_id, "user_in_gban")).format(mention)
	if until != 0:
		text += (await tl(chat_id, "restrict_time_left")).format(time_left(until))
	if check.reason:
		text += (await tl(chat_id, "blacklist_reason")).format(check.reason)
	await m.reply_text(text)

@Mayuri.on_message(filters.group, group=106)
async def gmute_watcher(c,m):
	chat_id = m.chat.id
	user_id = m.from_user.id
	mention = m.from_user.mention
	now = time.time()
	if await check_admin(chat_id,user_id):
		return
	check = sql.check_gmute(user_id)
	if not check:
		return
	until = check.until
	if until != 0:
		if until > now:
			if until-now < 40:
				until = now+40
			await c.restrict_chat_member(chat_id, user_id, ChatPermissions(), datetime.fromtimestamp(until))
		else:
			return sql.rm_from_gmute(user_id)
	else:
		await c.restrict_chat_member(chat_id, user_id, ChatPermissions())
	text = (await tl(chat_id, "user_in_gmute")).format(mention)
	if until != 0:
		text += (await tl(chat_id, "restrict_time_left")).format(time_left(until))
	if check.reason:
		text += (await tl(chat_id, "blacklist_reason")).format(check.reason)
	await m.reply_text(text)

@Mayuri.on_message(filters.group, group=107)
async def gdmute_watcher(c,m):
	user_id = m.from_user.id
	now = time.time()
	check = sql.check_gdmute(user_id)
	if not check:
		return
	until = check.until
	if until != 0 and until <= now:
		return sql.rm_from_gdmute(user_id)
	await m.delete()

@Mayuri.on_message(filters.group, group=108)
async def chat_watcher(c,m):
	if m.chat.type == enums.ChatType.PRIVATE:
		return
	chat_id = m.chat.id
	chat_name = m.chat.username
	check = sql.check_chat(chat_id)
	if not check:
		return sql.add_chat(chat_id, chat_name)
	if check.chat_name != chat_name:
		return sql.add_chat(chat_id, chat_name)
