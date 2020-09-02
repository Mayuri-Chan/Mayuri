import os

from mayuri import Command
from mayuri.modules.disableable import DisableAbleHandler, CheckDisable
from pyrogram import filters

async def stickerid(client,message):
	chat_id = message.chat.id
	check = CheckDisable(chat_id, message.text)
	if check:
		return

	if message.reply_to_message and message.reply_to_message.sticker:
		await message.reply_text("Id sticker yang anda balas :\n{}".format(message.reply_to_message.sticker.file_id))
	else:
		await message.reply_text("Anda harus membalas pesan sticker untuk menggunakan perintah ini!")

async def getsticker(client,message):
	chat_id = message.chat.id
	check = CheckDisable(chat_id, message.text)
	if check:
		return

	if message.reply_to_message and message.reply_to_message.sticker:
		file = message.reply_to_message.sticker
		await client.download_media(file, file_name='images/sticker.png')
		await message.reply_document(document=open('images/sticker.png', 'rb'))
		os.remove("images/sticker.png")
	else:
		await message.reply_text("Anda harus membalas pesan sticker untuk menggunakan perintah ini!")




DisableAbleHandler(stickerid,filters.command("stickerid", Command),'stickerid')
DisableAbleHandler(getsticker,filters.command("getsticker", Command),'getsticker')
