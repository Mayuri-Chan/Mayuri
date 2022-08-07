import asyncio
import time

from mayuri import PREFIX
from mayuri.db import admin as sql
from mayuri.mayuri import Mayuri
from mayuri.utils.filters import admin_only
from mayuri.utils.lang import tl
from pyrogram import enums, filters
from pyrogram.errors import FloodWait

__PLUGIN__ = "admin"
__HELP__ = "admin_help"

@Mayuri.on_message(filters.group, group=100)
async def adminlist_watcher(c,m):
	chat_id = m.chat.id
	current_time = int(time.time())
	last_sync = sql.get_last_sync(chat_id)
	if last_sync != 'NA':
		if int(last_sync.last_sync) > current_time-21600:
			return
		sql.remove_admin_list(chat_id)
	try:
		all_admin = c.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
	except FloodWait as e:
		await asyncio.sleep(e.value)
	async for admin in all_admin:
		await sql.add_admin_to_list(chat_id,admin.user.id,admin.user.username)
	sql.update_last_sync(chat_id,current_time)

async def check_admin(chat_id, user_id):
	data = sql.check_admin(str(chat_id),user_id)
	if data:
		return True
	return False

@Mayuri.on_message(filters.command("admincache", PREFIX) & admin_only)
async def admincache(c,m):
	chat_id = m.chat.id
	r = await m.reply_text(await tl(chat_id, "refreshing_admin"))
	current_time = int(time.time())
	sql.remove_admin_list(chat_id)
	try:
		all_admin = c.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
	except FloodWait as e:
		await asyncio.sleep(e.value)
	async for admin in all_admin:
		await sql.add_admin_to_list(chat_id,admin.user.id,admin.user.username)
	sql.update_last_sync(chat_id,current_time)
	await r.edit(await tl(chat_id, "admin_refreshed"))
