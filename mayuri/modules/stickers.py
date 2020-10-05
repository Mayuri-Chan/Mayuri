import os
import math
import imghdr

from mayuri import Command, AddHandler, TOKEN
from mayuri.modules.disableable import disableable
from pyrogram import filters
#from pyrogram.raw.types import InputStickerSetItem, InputStickerSetShortName
#from pyrogram.raw.functions.stickers import AddStickerToSet, CreateStickerSet

from PIL import Image

from telegram import Bot as tg
from telegram import TelegramError

__MODULE__ = "Stickers"
__HELP__ = """
[Stickers]
> `/stickerid`
Mendapatkan id dari sticker yang dibalas

> `/getsticker`
Untuk mendapatkan sticker yang dibalas dalam bentuk gambar (png)

> `/kang`
Untuk menambahkan sticker/gambar ke sticker pack
"""

updater = tg(TOKEN)

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
		await message.reply_text("Gunakan fitur ini dengan bijak!\nSilahkan cek gambar dibawah ini :)")
		await client.download_media(file, file_name='images/sticker.png')
		await message.reply_photo(photo=open('images/sticker.png', 'rb'))
		await message.reply_document(document=open('images/sticker.png', 'rb'))
		os.remove("images/sticker.png")
	else:
		await message.reply_text("Anda harus membalas pesan sticker untuk menggunakan perintah ini!")

@disableable
async def kang(client,message):
	args = (message.text).split()
	msg = await message.reply_text("Memproses...")
	user = message.from_user
	bot_username = (await client.get_me()).username
	packnum = 0
	packname = "c" + str(user.id) + "_by_"+bot_username
	packname_found = 0
	max_stickers = 120
	while packname_found == 0:
		try:
			stickerset = updater.get_sticker_set(packname)
			if len(stickerset.stickers) >= max_stickers:
					packnum += 1
					packname = "c" + str(packnum) + "_" + str(user.id) + "_by_"+bot_username
			else:
				packname_found = 1
		except TelegramError as e:
			if e.message == "Stickerset_invalid":
				packname_found = 1
	kangsticker = "images/kangsticker.png"
	if message.reply_to_message:
		if message.reply_to_message.sticker:
			file_id = message.reply_to_message.sticker.file_id
		elif message.reply_to_message.photo:
			file_id = message.reply_to_message.photo.file_id
		elif message.reply_to_message.document:
			file_id = message.reply_to_message.document.file_id
		else:
			await msg.edit("Itu tidak dapat di Kang")
			return
		await msg.edit("Mengunduh...")
		await client.download_media(file_id,file_name='images/kangsticker.png')
		image_type = imghdr.what(kangsticker)
		if image_type != 'jpeg' and image_type != 'png' and image_type != 'webp':
			await msg.edit("Format gambar tidak didukung! ({})".format(image_type))
			return
		if len(args) > 1:
			sticker_emoji = str(args[1])
		elif message.reply_to_message.sticker and message.reply_to_message.sticker.emoji:
			sticker_emoji = message.reply_to_message.sticker.emoji
		else:
			sticker_emoji = "🤔"
		try:
			im = Image.open(kangsticker)
			maxsize = (512, 512)
			if (im.width and im.height) < 512:
				size1 = im.width
				size2 = im.height
				if im.width > im.height:
					scale = 512/size1
					size1new = 512
					size2new = size2 * scale
				else:
					scale = 512/size2
					size1new = size1 * scale
					size2new = 512
				size1new = math.floor(size1new)
				size2new = math.floor(size2new)
				sizenew = (size1new, size2new)
				im = im.resize(sizenew)
			else:
				im.thumbnail(maxsize)
			if not message.reply_to_message.sticker:
				im.save(kangsticker, "PNG")
			updater.add_sticker_to_set(user_id=user.id, name=packname,
									png_sticker=open('images/kangsticker.png', 'rb'), emojis=sticker_emoji)
			await msg.edit("Sticker ditambahkan ke [pack](t.me/addstickers/{})\nEmojinya adalah: ```{}```".format(packname, sticker_emoji))
		except OSError as e:
			await message.reply_text("Saya hanya bisa kang gambar.")
			print(e)
			return
		except TelegramError as e:
			if e.message == "Stickerset_invalid":
				await msg.edit("Membuat stickerpack...")
				await makepack_internal(msg, user, open('images/kangsticker.png', 'rb'), sticker_emoji, updater, packname, packnum)
			elif e.message == "Sticker_png_dimensions":
				im.save(kangsticker, "PNG")
				updater.add_sticker_to_set(user_id=user.id, name=packname,
										png_sticker=open('images/kangsticker.png', 'rb'), emojis=sticker_emoji)
				await msg.edit("Sticker ditambahkan ke [pack](t.me/addstickers/{})\nEmojinya adalah: ```{}```".format(packname, sticker_emoji))
			elif e.message == "Invalid sticker emojis":
				await msg.edit("Emoji salah/tidak didukung.")
			elif e.message == "Stickers_too_much":
				await msg.edit("Sticker pack anda sudah penuh. Press F to pay respect")
			elif e.message == "Internal Server Error: sticker set not found (500)":
				await msg.edit("Sticker ditambahkan ke [pack](t.me/addstickers/{})\nEmojinya adalah: ```{}```".format(packname, sticker_emoji))
			print(e)
	else:
		packs = "Please reply to a sticker, or image to kang it!\nOh, by the way. here are your packs:\n"
		if packnum > 0:
			firstpackname = "c" + str(user.id) + "_by_"+bot_username
			for i in range(0, packnum + 1):
				if i == 0:
					packs += f"[pack](t.me/addstickers/{firstpackname})\n"
				else:
					packs += f"[pack{i}](t.me/addstickers/{packname})\n"
		else:
			packs += f"[pack](t.me/addstickers/{packname})"
		await msg.edit(packs)
	if os.path.isfile("images/kangsticker.png"):
		os.remove("images/kangsticker.png")

'''
@disableable
async def kang(client,message):
	args = (message.text).split()
	msg = await message.reply_text("Memproses...")
	user = message.from_user
	bot_username = (await client.get_me()).username
	packname = "c" + str(user.id) + "_by_"+bot_username
	peer_user = app.resolve_peer(user.id)
	stickerset = InputStickerSetShortName(short_name=packname)
	max_stickers = 120
	kangsticker = "images/kangsticker.png"
	if message.reply_to_message:
		if message.reply_to_message.sticker:
			file_id = message.reply_to_message.sticker.file_id
		elif message.reply_to_message.photo:
			file_id = message.reply_to_message.photo.file_id
		elif message.reply_to_message.document:
			file_id = message.reply_to_message.document.file_id
		else:
			await msg.edit("Itu tidak dapat di Kang")
			return
		await msg.edit("Mengunduh...")
		await client.download_media(file_id,file_name='images/kangsticker.png')
		image_type = imghdr.what(kangsticker)
		if image_type != 'jpeg' and image_type != 'png' and image_type != 'webp':
			await msg.edit("Format gambar tidak didukung! ({})".format(image_type))
			return
		if len(args) > 1:
			sticker_emoji = str(args[1])
		elif message.reply_to_message.sticker and message.reply_to_message.sticker.emoji:
			sticker_emoji = message.reply_to_message.sticker.emoji
		else:
			sticker_emoji = "🤔"
		try:
			im = Image.open(kangsticker)
			maxsize = (512, 512)
			if (im.width and im.height) < 512:
				size1 = im.width
				size2 = im.height
				if im.width > im.height:
					scale = 512/size1
					size1new = 512
					size2new = size2 * scale
				else:
					scale = 512/size2
					size1new = size1 * scale
					size2new = 512
				size1new = math.floor(size1new)
				size2new = math.floor(size2new)
				sizenew = (size1new, size2new)
				im = im.resize(sizenew)
			else:
				im.thumbnail(maxsize)
			if not message.reply_to_message.sticker:
				im.save(kangsticker, "PNG")
			sticker = InputStickerSetItem(document=open('images/kangsticker.png', 'rb'),emoji=sticker_emoji)
			await app.send(AddStickerToSet(stickerset=stickerset,sticker=sticker))
			await msg.edit("Sticker ditambahkan ke [pack](t.me/addstickers/{})\nEmojinya adalah: ```{}```".format(packname, sticker_emoji))
		except:
			title = "{} mayuri\'s pack".format(user.first_name)
			await app.send(CreateStickerSet(user_id=peer_user,title=title,short_name=packname,stickers=sticker))
			await msg.edit("Sticker pack successfully created. Get it [here](t.me/addstickers/%s)" % packname)
	else:
		packs = "Please reply to a sticker, or image to kang it!\nOh, by the way. here are your packs:\n"
		packs += f"[pack](t.me/addstickers/{packname})"
		await msg.edit(packs)
	if os.path.isfile("images/kangsticker.png"):
		os.remove("images/kangsticker.png")
'''

async def makepack_internal(msg, user, png_sticker, emoji, updater, packname, packnum):
	name = user.first_name
	name = name[:50]
	try:
		extra_version = ""
		if packnum > 0:
			extra_version = " " + str(packnum)
		success = updater.create_new_sticker_set(user.id, packname, f"{name}'s mayuri pack" + extra_version,
											 png_sticker=png_sticker,
											 emojis=emoji)
	except TelegramError as e:
		print(e)
		if e.message == "Sticker set name is already occupied":
			await msg.edit("Your pack can be found [here](t.me/addstickers/%s)" % packname)
		elif e.message == "Peer_id_invalid":
			await msg.edit("Contact me in PM first.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
				text="Start", url=f"t.me/{bot_username}")]]))
		elif e.message == "Internal Server Error: created sticker set not found (500)":
				await msg.edit("Sticker pack successfully created. Get it [here](t.me/addstickers/%s)" % packname)
		return

	if success:
		await msg.edit("Sticker pack successfully created. Get it [here](t.me/addstickers/%s)" % packname)
	else:
		await msg.edit("Failed to create sticker pack. Possibly due to blek mejik.")

AddHandler(stickerid,filters.command("stickerid", Command))
AddHandler(getsticker,filters.command("getsticker", Command))
AddHandler(kang,filters.command("kang", Command))
