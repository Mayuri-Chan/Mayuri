import asyncio

from functools import wraps
from mayuri import DISABLEABLE, PREFIX
from pyrogram import enums, filters
from pyrogram.errors import FloodWait

async def owner_check(_, c, m):
	if m.sender_chat:
		return False
	user_id = m.from_user.id
	if user_id == c.config['bot']['OWNER']:
		return True
	return False

async def sudo_check(_, c, m):
	if m.sender_chat:
		return False
	user_id = m.from_user.id
	db = c.db["bot_settings"]
	check = await db.find_one({'name': 'sudo_list'})
	owner = await owner_check(_, c, m)
	if (check and user_id in check['list']) or owner:
		return True
	return False

async def admin_check(_, c, m):
	if m.sender_chat:
		try:
			curr_chat = await c.get_chat(m.chat.id)
		except FloodWait as e:
			asyncio.sleep(e.value)
		if m.sender_chat.id == m.chat.id: # Anonymous admin
			return True
		if curr_chat.linked_chat:
			if (
				m.sender_chat.id == curr_chat.linked_chat.id and
				not m.forward_from
			): # Linked channel owner
				return True
		return False
	chat_id = m.chat.id
	user_id = m.from_user.id
	db = c.db["admin_list"]
	check = await db.find_one({"chat_id": chat_id})
	if check and user_id in check["list"]:
		return True
	return False

def disable(func):
	wraps(func)
	name = func.__name__
	cmd = name[4:]
	if cmd not in DISABLEABLE:
		DISABLEABLE.append(cmd)

	async def decorator(c, m):
		if not m.text:
			return False
		text = (m.text.split(None, 1))[0]
		text = text.replace("@{}".format(c.me.username), '')
		if text.startswith(tuple(PREFIX)) and text[1:] == cmd:
			if m.chat.type == enums.ChatType.PRIVATE:
				return await func(c,m)
			if await admin_check(None, c, m):
				return await func(c,m)
			db = c.db["chat_settings"]
			disabled = await db.find_one({"chat_id": m.chat.id})
			if disabled and "disabled_list" in disabled and cmd in disabled['disabled_list']:
				return
			await func(c,m)
	return decorator


owner_only = filters.create(owner_check)
sudo_only = filters.create(sudo_check)
admin_only = filters.create(admin_check)
