import array

from functools import wraps

from mayuri import Command, AddHandler, OWNER, admin
from mayuri.modules.sql import approve as sql
from pyrogram import filters
from pyrogram.errors import RPCError

async def approved(chat_id):
	approve = sql.approve_list(chat_id)
	approve_list = []
	for user_id in approve:
		approve_list.append(user_id.user_id)
	return approve_list

@admin
async def approvels(client,message):
	text = "Daftar whitelist di grup ini:"
	chat_id = message.chat.id
	approve_list = await approved(chat_id)
	for user_id in approve_list:
		user = await client.get_users(user_id.user_id)
		mention = user.mention
		text += "\n - {}".format(mention)
	await message.reply_text(text)

@admin
async def add_approve(client,message):
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

	sql.add_to_approve(chat_id,user_id)
	text = "User {} telah ditambahkan ke daftar whitelist".format(mention)
	await message.reply_text(text)

@admin
async def rm_approve(client,message):
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

	sql.rm_from_approve(chat_id,user_id)
	text = "User {} telah di hapus dari whitelist".format(mention)
	await message.reply_text(text)

AddHandler(add_approve,filters.command("approve", Command))
AddHandler(rm_approve,filters.command("unapprove", Command))
AddHandler(approvels,filters.command("approvels", Command))
