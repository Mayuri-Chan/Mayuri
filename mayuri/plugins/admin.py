import asyncio
import time

from mayuri import PREFIX
from mayuri.db import admin as sql, approve as asql
from mayuri.mayuri import Mayuri
from mayuri.utils.filters import admin_only
from mayuri.utils.lang import tl
from pyrogram import enums, filters
from pyrogram.errors import FloodWait, RPCError

__PLUGIN__ = "admin"
__HELP__ = "admin_help"

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

@Mayuri.on_message(filters.command("approvels", PREFIX) & admin_only)
async def approvels(c,m):
	chat_id = m.chat.id
	text = await tl(chat_id, 'admin_approved_list')
	approve_list = asql.approve_list(chat_id)
	if approve_list:
		for approved in approve_list:
			user = await c.get_users(approved.user_id)
			mention = user.mention
			text += "\n - {}".format(mention)
		return await m.reply_text(text)
	m.reply_text(await tl(chat_id, 'admin_no_approved'))

@Mayuri.on_message(filters.command("approve", PREFIX) & admin_only)
async def approve(c,m):
	chat_id = m.chat.id
	if m.reply_to_message:
		user_id = m.reply_to_message.from_user.id
		mention = m.reply_to_message.from_user.mention
	else:
		args = m.text.split(None,1)
		try:
			user = await c.get_users(args[1])
			user_id = user.id
			mention = user.mention
		except RPCError:
			return await m.reply_text(await tl(chat_id, 'need_user_id'))
	asql.add_to_approve(chat_id,user_id)
	text = (await tl(chat_id, "admin_user_added_to_approve")).format(mention)
	await m.reply_text(text)

@Mayuri.on_message(filters.command("unapprove", PREFIX) & admin_only)
async def unapprove(c,m):
	chat_id = m.chat.id
	if m.reply_to_message:
		user_id = m.reply_to_message.from_user.id
		mention = m.reply_to_message.from_user.mention
	else:
		args = m.text.split(None,1)
		try:
			user = await c.get_users(args[1])
			user_id = user.id
			mention = user.mention
		except RPCError:
			return await m.reply_text(await tl(chat_id, 'need_user_id'))
	asql.rm_from_approve(chat_id,user_id)
	text = (await tl(chat_id, "admin_user_removed_to_approve")).format(mention)
	await m.reply_text(text)

async def zombies_task(c,m):
	chat_id = m.chat.id
	msg = await m.reply_text(await tl(chat_id, "search_zombies"))
	await m.delete()
	count = 0
	users = []
	try:
		chat_members = c.get_chat_members(chat_id)
	except FloodWait as e:
		await asyncio.sleep(e.value)
	async for member in chat_members:
		if member.user.is_deleted and not await check_admin(chat_id, member.user.id):
			count = count+1
			users.append(member.user.id)

	if count == 0:
		await msg.edit(await tl(chat_id, "no_zombies"))
	else:
		await msg.edit((await tl(chat_id, "found_zombies")).format(count))
		for user in users:
			await c.ban_chat_member(chat_id,user)
		await msg.edit((await tl(chat_id, "zombies_cleaned")).format(count))
	await asyncio.sleep(2)
	await msg.delete()

@Mayuri.on_message(filters.command("zombies", PREFIX) & admin_only)
async def zombies(c,m):
	asyncio.create_task(zombies_task(c,m))
