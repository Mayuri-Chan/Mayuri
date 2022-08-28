from mayuri import OWNER, PREFIX
from mayuri.db import sudo as sql
from mayuri.mayuri import Mayuri
from mayuri.utils.filters import owner_only
from mayuri.utils.lang import tl
from pyrogram import filters
from pyrogram.errors import RPCError

@Mayuri.on_message(filters.command("addsudo", PREFIX) & owner_only)
async def add_sudo(c,m):
	chat_id = m.chat.id
	if m.reply_to_message:
		user_id = m.reply_to_message.from_user.id
		mention = m.reply_to_message.from_user.mention
	else:
		args = m.text.split(None,2)
		try:
			user = await c.get_users(args[1])
			user_id = user.id
			mention = user.mention
		except RPCError:
			await m.reply_text(await tl(chat_id, "not_user"))
			return
	sql.add_to_sudo(user_id)
	text = (await tl(chat_id, "added_to_sudo")).format(mention)
	await m.reply_text(text)

@Mayuri.on_message(filters.command("rmsudo", PREFIX) & owner_only)
async def rm_sudo(c,m):
	chat_id = m.chat.id
	if m.reply_to_message:
		user_id = m.reply_to_message.from_user.id
		mention = m.reply_to_message.from_user.mention
	else:
		args = m.text.split(None,2)
		try:
			user = await c.get_users(args[1])
			user_id = user.id
			mention = user.mention
		except RPCError:
			await m.reply_text(await tl(chat_id, "not_user"))
			return

	sql.rm_from_sudo(user_id)
	text = (await tl(chat_id, "removed_to_sudo")).format(mention)
	await m.reply_text(text)

@Mayuri.on_message(filters.command("sudols", PREFIX) & owner_only)
async def sudols(c,m):
	chat_id = m.chat.id
	text = await tl(chat_id, "sudo_ls")
	sudo_list = sql.sudo_list()
	for sudo in sudo_list:
		user = await c.get_users(sudo.user_id)
		mention = user.mention
		text += "\n - {}".format(mention)
	await m.reply_text(text)

async def check_sudo(user_id):
	user_id = user_id
	check = sql.check_sudo(user_id)
	if check or user_id == OWNER:
		return True
	return False
