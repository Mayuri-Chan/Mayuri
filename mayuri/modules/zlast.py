from mayuri import AddHandler
from mayuri.modules.anti_ubot import bl_ubot
from mayuri.modules.blacklist import bl
from pyrogram import filters

async def last(client,message):
	await bl_ubot(client,message)
	await bl(client,message)

AddHandler(last,filters.text & filters.group)