import os

from mayuri import Command, AddHandler
from mayuri.modules.disableable import disableable
from pyrogram import filters

@disableable
async def stickerid(client,message):
	chat_id = message.chat.id
	if message.reply_to_message and message.reply_to_message.sticker:
		await message.reply_text("Id sticker yang anda balas :\n{}".format(message.reply_to_message.sticker.file_id))
	else:
		await message.reply_text("Anda harus membalas pesan sticker untuk menggunakan perintah ini!")

@disableable
async def getsticker(client,message):
	chat_id = message.chat.id
	if message.reply_to_message and message.reply_to_message.sticker:
		file = message.reply_to_message.sticker
		await client.download_media(file, file_name='images/sticker.png')
		await message.reply_document(document=open('images/sticker.png', 'rb'))
		os.remove("images/sticker.png")
	else:
		await message.reply_text("Anda harus membalas pesan sticker untuk menggunakan perintah ini!")

AddHandler(stickerid,filters.command("stickerid", Command))
AddHandler(getsticker,filters.command("getsticker", Command))
