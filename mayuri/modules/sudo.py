import array

from functools import wraps

from mayuri import Command, AddHandler, OWNER
from mayuri.modules.sql import sudo as sql
from pyrogram import filters
from pyrogram.errors import RPCError

SUDO = []
sudo_list = sql.sudo_list()
for sudo in sudo_list:
	SUDO.append(sudo.user_id)

def sudo(func):
	wraps(func)
	async def decorator(client,message):
		user_id = message.from_user.id
		if user_id not in OWNER and user_id not in SUDO:
			return
		else:
			await func(client,message)
	return decorator

async def add_sudo(client,message):
	chat_id = message.chat.id
	if message.reply_to_message:
		user_id = message.reply_to_message.from_user.id
		mention = message.reply_to_message.from_user.mention
	else:
		args = message.text.split(None,2)
		try:
			user = await client.get_users(args[1])
			user_id = user.id
			mention = user.mention
		except RPCError:
			await message.reply_text("Itu bukan user!")
			return

	SUDO.append(user_id)
	sql.add_to_sudo(user_id)
	text = "User {} telah ditambahkan ke SUDO".format(mention)
	await message.reply_text(text)

async def rm_sudo(client,message):
	chat_id = message.chat.id
	if message.reply_to_message:
		user_id = message.reply_to_message.from_user.id
		mention = message.reply_to_message.from_user.mention
	else:
		args = message.text.split(None,2)
		try:
			user = await client.get_users(args[1])
			user_id = user.id
			mention = user.mention
		except RPCError:
			await message.reply_text("Itu bukan user!")
			return

	sql.rm_from_sudo(user_id)
	text = "User {} telah di hapus dari SUDO".format(mention)
	await message.reply_text(text)

AddHandler(add_sudo,filters.user(OWNER) & filters.command("addsudo", Command))
AddHandler(rm_sudo,filters.user(OWNER) & filters.command("rmsudo", Command))
