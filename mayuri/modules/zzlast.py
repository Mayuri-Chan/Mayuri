from mayuri import AddHandler
from mayuri.modules.anti_ubot import bl_ubot
from mayuri.modules.blacklist import bl
from mayuri.modules.blstickers import blsticker
from mayuri.modules.blpack import blpack
from mayuri.modules.filters import filtr
from mayuri.modules.globals import addchat, check_gban, check_gmute
from pyrogram import filters

async def last(client,message):
	await addchat(client,message)
	await check_gban(client,message)
	await check_gmute(client,message)
	if message.sticker:
		await blsticker(client,message)
		await blpack(client,message)
	elif message.text or message.caption:
		await bl_ubot(client,message)
		await filtr(client,message)
		await bl(client,message)

AddHandler(last,filters.group)
