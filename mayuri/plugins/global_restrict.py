import re
import time

from datetime import datetime
from mayuri import PREFIX
from mayuri.mayuri import Mayuri
from mayuri.util.filters import sudo_only
from mayuri.util.string import split_quotes
from mayuri.util.time import create_time, time_left, tl_time
from pyrogram import enums, filters
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import ChatPermissions

@Mayuri.on_message(filters.group, group=1)
async def chat_watcher(c,m):
	db = c.db["chat_list"]
	chat_id = m.chat.id
	await db.update_one({'chat_id': chat_id},{"$set": {'chat_username': m.chat.username, 'chat_name': m.chat.title}}, upsert=True)

async def gban_task(c,m):
	db = c.db["gban_list"]
	chat_db = c.db["chat_list"]
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
			if re.match(r"([0-9]{1,})([dhms])$", text[1].lower()):
				duration = text[1].lower()
				if len(text) > 2:
					reason = text[2]
			elif re.match(r"([0-9]{1,})([dhms])$", extracted[0].lower()):
				duration = extracted[0].lower()
				if len(extracted) > 1:
					reason = extracted[1]
			else:
				reason = text[1]
	else:
		if len(text) > 1:
			extracted = split_quotes(text[1])
			if len(extracted) > 1:
				user_id = extracted[0]
				extracted1 = split_quotes(extracted[1])
				if re.match(r"([0-9]{1,})([dhms])$", extracted[1].lower()):
					duration = extracted[1].lower()
				elif len(extracted1) > 1 and re.match(r"([0-9]{1,})([dhms])$", extracted1[0].lower()):
					duration = extracted1[0].lower()
					reason = extracted1[1].lower()
				else:
					reason = extracted[1].lower()
			else:
				user_id = text[1]
		else:
			return await msg.edit_text(await c.tl(chat_id, "need_user_id"))
		try:
			user = await c.get_users(user_id)
		except FloodWait as e:
			await asyncio.sleep(e.value)
		except RPCError:
			return await msg.edit_text(await c.tl(chat_id, "need_user_id"))
	if user.id == c.config['bot']['OWNER']:
		return await msg.edit_text(await c.tl(chat_id, "why_gban_owner"))
	if await c.check_sudo(user.id):
		return await msg.edit_text(await c.tl(chat_id, "why_gban_sudo"))
	if duration:
		until = create_time(duration)
	check = await db.find_one({'user_id': user.id})
	await db.update_one({'user_id': user.id}, {"$set": {'reason': reason, 'until': until}}, upsert=True)
	async for chat in chat_db.find():
		if await c.check_admin(chat["chat_id"],user.id) or await c.check_approved(chat["chat_id"], user.id):
			continue
		try:
			if duration:
				await c.ban_chat_member(chat["chat_id"], user.id, datetime.fromtimestamp(until))
			else:
				await c.ban_chat_member(chat["chat_id"], user.id)
		except RPCError:
			print(RPCError)
	text = (await c.tl(chat_id, "gbanned")).format(user.mention)
	log = await c.tl(chat_id, "new_gban")
	log += (await c.tl(chat_id, "infouser_sudo")).format(sudo_mention)
	log += (await c.tl(chat_id, "infouser_id")).format(user.id)
	log += (await c.tl(chat_id, "infouser_firstname")).format(user.first_name)
	log += (await c.tl(chat_id, "infouser_lastname")).format(user.last_name)
	log += (await c.tl(chat_id, "infouser_name")).format(user.username)
	log += (await c.tl(chat_id, "infouser_link")).format(user.id)
	if duration:
		log += (await c.tl(chat_id, "infouser_duration")).format(tl_time(duration))
		text += (await c.tl(chat_id, "blacklist_for")).format(tl_time(duration))
	if reason:
		log += (await c.tl(chat_id, "blacklist_reason")).format(reason)
		text += (await c.tl(chat_id, "blacklist_reason")).format(reason)
	await c.send_message(chat_id=c.config['global_restrict']['LOG_CHAT'], text=log)
	await msg.edit_text(text)

@Mayuri.on_message(filters.command("gban", PREFIX) & sudo_only)
async def gban(c,m):
	await c.loop.create_task(gban_task(c,m))

@Mayuri.on_message(filters.group, group=105)
async def gban_watcher(c,m):
	db = c.db["gban_list"]
	if m.sender_chat:
		return
	chat_id = m.chat.id
	user_id = m.from_user.id
	mention = m.from_user.mention
	now = time.time()
	if await c.check_admin(chat_id,user_id) or await c.check_approved(chat_id, user_id):
		return
	check = await db.find_one({'user_id': user_id})
	if not check:
		return
	until = check['until']
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
		text += (await tl(chat_id, "blacklist_reason")).format(check['reason'])
	await m.reply_text(text)

async def ungban_task(c,m):
	db = c.db["gban_list"]
	chat_db = c.db["chat_list"]
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
			return await msg.edit_text(await c.tl(chat_id, "need_user_id"))
		try:
			user = await c.get_users(user_id)
		except FloodWait as e:
			await asyncio.sleep(e.value)
		except RPCError:
			return await msg.edit_text(await c.tl(chat_id, "need_user_id"))
	await db.delete_one({'user_id': user.id})
	async for chat in chat_db.find():
		if await c.check_admin(chat['chat_id'],user.id):
			continue
		try:
			await c.unban_chat_member(chat['chat_id'], user.id)
		except RPCError:
			print(RPCError)
	text = (await c.tl(chat_id, "ungbanned")).format(user.mention)
	log = await c.tl(chat_id, "new_ungban")
	log += (await c.tl(chat_id, "infouser_sudo")).format(sudo_mention)
	log += (await c.tl(chat_id, "infouser_id")).format(user.id)
	log += (await c.tl(chat_id, "infouser_firstname")).format(user.first_name)
	log += (await c.tl(chat_id, "infouser_lastname")).format(user.last_name)
	log += (await c.tl(chat_id, "infouser_name")).format(user.username)
	log += (await c.tl(chat_id, "infouser_link")).format(user.id)
	await c.send_message(chat_id=c.config['global_restrict']['LOG_CHAT'], text=log)
	await msg.edit_text(text)

@Mayuri.on_message(filters.command("ungban", PREFIX) & sudo_only)
async def ungban(c,m):
	await c.loop.create_task(ungban_task(c,m))

async def gmute_task(c,m):
	db = c.db["gmute_list"]
	chat_db = c.db["chat_list"]
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
			if re.match(r"([0-9]{1,})([dhms])$", text[1].lower()):
				duration = text[1].lower()
				if len(text) > 2:
					reason = text[2]
			elif re.match(r"([0-9]{1,})([dhms])$", extracted[0].lower()):
				duration = extracted[0].lower()
				if len(extracted) > 1:
					reason = extracted[1]
			else:
				reason = text[1]
	else:
		if len(text) > 1:
			extracted = split_quotes(text[1])
			if len(extracted) > 1:
				user_id = extracted[0]
				extracted1 = split_quotes(extracted[1])
				if re.match(r"([0-9]{1,})([dhms])$", extracted[1].lower()):
					duration = extracted[1].lower()
				elif len(extracted1) > 1 and re.match(r"([0-9]{1,})([dhms])$", extracted1[0].lower()):
					duration = extracted1[0].lower()
					reason = extracted1[1].lower()
				else:
					reason = extracted[1].lower()
			else:
				user_id = text[1]
		else:
			return await msg.edit_text(await c.tl(chat_id, "need_user_id"))
		try:
			user = await c.get_users(user_id)
		except FloodWait as e:
			await asyncio.sleep(e.value)
		except RPCError:
			return await msg.edit_text(await c.tl(chat_id, "need_user_id"))
	if user.id == c.config['bot']['OWNER']:
		return await msg.edit_text(await c.tl(chat_id, "why_gmute_owner"))
	if await c.check_sudo(user.id):
		return await msg.edit_text(await c.tl(chat_id, "why_gmute_sudo"))
	if duration:
		until = create_time(duration)
	check = await db.find_one({'user_id': user.id})
	await db.update_one({'user_id': user.id}, {"$set": {'reason': reason, 'until': until}}, upsert=True)
	async for chat in chat_db.find():
		if await c.check_admin(chat["chat_id"],user.id) or await c.check_approved(chat["chat_id"], user.id):
			continue
		try:
			if duration:
				await c.restrict_chat_member(chat["chat_id"], user.id, ChatPermissions(), datetime.fromtimestamp(until))
			else:
				await c.restrict_chat_member(chat["chat_id"], user.id, ChatPermissions())
		except RPCError:
			print(RPCError)
	text = (await c.tl(chat_id, "gmuted")).format(user.mention)
	log = await c.tl(chat_id, "new_gmute")
	log += (await c.tl(chat_id, "infouser_sudo")).format(sudo_mention)
	log += (await c.tl(chat_id, "infouser_id")).format(user.id)
	log += (await c.tl(chat_id, "infouser_firstname")).format(user.first_name)
	log += (await c.tl(chat_id, "infouser_lastname")).format(user.last_name)
	log += (await c.tl(chat_id, "infouser_name")).format(user.username)
	log += (await c.tl(chat_id, "infouser_link")).format(user.id)
	if duration:
		log += (await c.tl(chat_id, "infouser_duration")).format(tl_time(duration))
		text += (await c.tl(chat_id, "blacklist_for")).format(tl_time(duration))
	if reason:
		log += (await c.tl(chat_id, "blacklist_reason")).format(reason)
		text += (await c.tl(chat_id, "blacklist_reason")).format(reason)
	await c.send_message(chat_id=c.config['global_restrict']['LOG_CHAT'], text=log)
	await msg.edit_text(text)

@Mayuri.on_message(filters.command("gmute", PREFIX) & sudo_only)
async def gmute(c,m):
	await c.loop.create_task(gmute_task(c,m))

@Mayuri.on_message(filters.group, group=106)
async def gmute_watcher(c,m):
	db = c.db["gmute_list"]
	if m.sender_chat:
		return
	chat_id = m.chat.id
	user_id = m.from_user.id
	mention = m.from_user.mention
	now = time.time()
	if await c.check_admin(chat_id,user_id) or await c.check_approved(chat_id, user_id):
		return
	check = await db.find_one({'user_id': user_id})
	if not check:
		return
	until = check['until']
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
		text += (await tl(chat_id, "blacklist_reason")).format(check['reason'])
	await m.reply_text(text)

async def ungmute_task(c,m):
	db = c.db["gmute_list"]
	chat_db = c.db["chat_list"]
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
			return await msg.edit_text(await c.tl(chat_id, "need_user_id"))
		try:
			user = await c.get_users(user_id)
		except FloodWait as e:
			await asyncio.sleep(e.value)
		except RPCError:
			return await msg.edit_text(await c.tl(chat_id, "need_user_id"))
	await db.delete_one({'user_id': user.id})
	async for chat in chat_db.find():
		if await c.check_admin(chat["chat_id"],user.id):
			continue
		try:
			curr = (await c.get_chat(chat["chat_id"])).permissions
			await c.restrict_chat_member(chat["chat_id"],user.id, curr)
		except RPCError:
			print(RPCError)
	text = (await c.tl(chat_id, "ungmuted")).format(user.mention)
	log = await c.tl(chat_id, "new_ungmute")
	log += (await c.tl(chat_id, "infouser_sudo")).format(sudo_mention)
	log += (await c.tl(chat_id, "infouser_id")).format(user.id)
	log += (await c.tl(chat_id, "infouser_firstname")).format(user.first_name)
	log += (await c.tl(chat_id, "infouser_lastname")).format(user.last_name)
	log += (await c.tl(chat_id, "infouser_name")).format(user.username)
	log += (await c.tl(chat_id, "infouser_link")).format(user.id)
	await c.send_message(chat_id=c.config['global_restrict']['LOG_CHAT'], text=log)
	await msg.edit_text(text)

@Mayuri.on_message(filters.command("ungmute", PREFIX) & sudo_only)
async def ungmute(c,m):
	await c.loop.create_task(ungmute_task(c,m))
