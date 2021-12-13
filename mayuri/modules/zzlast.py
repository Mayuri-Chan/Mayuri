from mayuri import AddHandler
from mayuri.modules.anti_ubot import bl_ubot
from mayuri.modules.approve import approved
from mayuri.modules.blacklist import bl
from mayuri.modules.blimg import blimg
from mayuri.modules.blstickers import blsticker
from mayuri.modules.blpack import blpack
from mayuri.modules.filters import filtr
from mayuri.modules.globals import addchat, check_gban, check_gmute
from mayuri.modules.sudo import SUDO
from pyrogram import filters

async def last(client,message):
	if message.sender_chat:
		curr_chat = await client.get_chat(message.chat.id)
		if curr_chat.linked_chat:
			if message.sender_chat.id == curr_chat.linked_chat.id:
				return
			else:
				await message.delete()
				return
		else:
			await message.delete()
			return

	await addchat(client,message)
	chat_id = message.chat.id
	user_id = message.from_user.id
	approve_list = await approved(chat_id)
	if user_id in SUDO or user_id in approve_list:
		return
	await check_gban(client,message)
	await check_gmute(client,message)
	if message.sticker:
		await blsticker(client,message)
		await blpack(client,message)
	elif message.text or message.photo or message.video:
		await bl_ubot(client,message)
		await filtr(client,message)
		await bl(client,message)
		if message.photo:
			await blimg(client,message)

AddHandler(last,filters.group)
