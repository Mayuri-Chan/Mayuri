import array
from mayuri import Command, AddHandler, SUDO, OWNER
from mayuri.modules.sudo import sudo
from mayuri.modules.sql import globals_sql as sql
from pyrogram import filters
from pyrogram.errors import RPCError
from pyrogram.types import ChatPermissions

async def addchat(client,message):
	chat_id = message.chat.id
	chat_name = message.chat.username
	chat_list = sql.get_chatlist()
	if not sql.check_chatlist(chat_id):
		sql.add_to_chatlist(chat_id,chat_name)

@sudo
async def gban(client,message):
	chat_id = message.chat.id
	sudo_id = message.from_user.id
	if message.reply_to_message:
		args = message.text.split(None,1)
		user_id = message.reply_to_message.from_user.id
		mention = message.reply_to_message.from_user.mention
		if len(args) > 1:
			reason = args[1]
		else:
			reason = ''
	else:
		args = message.text.split(None,2)
		try:
			user = await client.get_users(args[1])
			user_id = user.id
			mention = user.mention
			if len(args) > 2:
				reason = args[2]
			else:
				reason = ''
		except RPCError:
			await message.reply_text("Itu bukan user!")
			return
	if user_id in SUDO:
		await message.reply_text("Kenapa saya harus ban salah satu SUDO saya secara global?")
		return
	if user_id in OWNER:
		await message.reply_text("Orang ini adalah Master saya, saya tidak akan melakukan apapun terhadap dia!")
		return
	chat_list = sql.get_chatlist()
	if chat_list:
		await message.reply_sticker("CAADBQADTwEAAmotjDNdb-SGNzP8rxYE")
		await message.reply_text("Its Global Banning Time...")
		msg = await client.send_message(chat_id, "Banning...")
		sql.add_to_gban(user_id,reason)
		for chat in chat_list:
			try:
				all = client.iter_chat_members(chat.chat_name, filter="administrators")
				admin_list = []
				async for admin in all:
					admin_list.append(admin.user.id)
					if user_id not in admin_list:
						await client.kick_chat_member(chat.chat_name,user_id)
			except RPCError as e:
				print("{} | {}".format(e,chat.chat_name))
		if reason:
			text = "User {} telah di ban secara global\nAlasan : {}".format(mention,reason)
		else:
			text = "User {} telah di ban secara global".format(mention)
		await msg.edit(text)

@sudo
async def ungban(client,message):
	chat_id = message.chat.id
	sudo_id = message.from_user.id
	if message.reply_to_message:
		args = message.text.split(None,1)
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

	chat_list = sql.get_chatlist()
	sql.rm_from_gban(user_id)
	if chat_list:
		msg = await client.send_message(chat_id, "Un-Banning...")
		for chat in chat_list:
			try:
				all = client.iter_chat_members(chat.chat_name, filter="administrators")
				admin_list = []
				async for admin in all:
					admin_list.append(admin.user.id)
					if user_id not in admin_list:
						await client.unban_chat_member(chat.chat_name,user_id)
			except RPCError as e:
				print("{} | {}".format(e,chat.chat_name))
		text = "User {} telah di unban secara global".format(mention)
		await msg.edit(text)

async def check_gban(client,message):
	user_id = message.from_user.id
	if user_id in SUDO or user_id in OWNER:
		return
	mention = message.from_user.mention
	chat_id = message.chat.id
	check = sql.check_gban(user_id)
	admin_list = []
	all = client.iter_chat_members(chat_id, filter="administrators")
	admin_list = []
	async for admin in all:
		admin_list.append(admin.user.id)
	if user_id in admin_list:
		return
	if check:
		text = "User {} ada daftar global ban dan telah di banned dari grup!".format(mention)
		if check.reason:
			text += "\nAlasan : {}".format(check.reason)
		await client.kick_chat_member(chat_id,user_id)
		await client.send_message(chat_id,text)

@sudo
async def gmute(client,message):
	chat_id = message.chat.id
	sudo_id = message.from_user.id
	if message.reply_to_message:
		args = message.text.split(None,1)
		user_id = message.reply_to_message.from_user.id
		mention = message.reply_to_message.from_user.mention
		if len(args) > 1:
			reason = args[1]
		else:
			reason = ''
	else:
		args = message.text.split(None,2)
		try:
			user = await client.get_users(args[1])
			user_id = user.id
			mention = user.mention
			if len(args) > 2:
				reason = args[2]
			else:
				reason = ''
		except RPCError:
			await message.reply_text("Itu bukan user!")
			return
	if user_id in SUDO:
		await message.reply_text("Kenapa saya harus membisukan salah satu SUDO saya secara global?")
		return
	if user_id in OWNER:
		await message.reply_text("Orang ini adalah Master saya, saya tidak akan melakukan apapun terhadap dia!")
		return
	chat_list = sql.get_chatlist()
	sql.add_to_gmute(user_id,reason)
	if chat_list:
		await message.reply_sticker("CAADBQADTwEAAmotjDNdb-SGNzP8rxYE")
		await message.reply_text("Its Global Muting Time...")
		msg = await client.send_message(chat_id, "Membisukan...")
		for chat in chat_list:
			try:
				all = client.iter_chat_members(chat.chat_name, filter="administrators")
				admin_list = []
				async for admin in all:
					admin_list.append(admin.user.id)
					if user_id not in admin_list:
						await client.restrict_chat_member(chat.chat_name,user_id, ChatPermissions())
			except RPCError as e:
				print("{} | {}".format(e,chat.chat_name))
		if reason:
			text = "User {} telah di mute secara global\nAlasan : {}".format(mention,reason)
		else:
			text = "User {} telah di mute secara global".format(mention)
		await msg.edit(text)

@sudo
async def ungmute(client,message):
	chat_id = message.chat.id
	sudo_id = message.from_user.id
	if message.reply_to_message:
		args = message.text.split(None,1)
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

	chat_list = sql.get_chatlist()
	sql.rm_from_gmute(user_id)
	if chat_list:
		msg = await client.send_message(chat_id, "Menyuarakan...")
		for chat in chat_list:
			try:
				all = client.iter_chat_members(chat.chat_name, filter="administrators")
				admin_list = []
				async for admin in all:
					admin_list.append(admin.user.id)
					if user_id not in admin_list:
						curr = (await client.get_chat(chat.chat_name)).permissions
						await client.restrict_chat_member(chat.chat_name,user_id, curr)
			except RPCError as e:
				print("{} | {}".format(e,chat.chat_name))
		text = "User {} telah di unmute secara global".format(mention)
		await msg.edit(text)

async def check_gmute(client,message):
	user_id = message.from_user.id
	if user_id in SUDO or user_id in OWNER:
		return
	mention = message.from_user.mention
	chat_id = message.chat.id
	check = sql.check_gmute(user_id)
	admin_list = []
	all = client.iter_chat_members(chat_id, filter="administrators")
	admin_list = []
	async for admin in all:
		admin_list.append(admin.user.id)
	if user_id in admin_list:
		return
	if check:
		text = "User {} ada daftar global mute dan telah di bisukan!".format(mention)
		if check.reason:
			text += "\nAlasan : {}".format(check.reason)
		await client.restrict_chat_member(chat.chat_name,user_id, ChatPermissions())
		await client.send_message(chat_id,text)

AddHandler(gban,filters.group & filters.command("gban", Command))
AddHandler(ungban,filters.group & filters.command("ungban", Command))
AddHandler(gmute,filters.group & filters.command("gmute", Command))
AddHandler(ungmute,filters.group & filters.command("ungmute", Command))
