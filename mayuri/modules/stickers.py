import os

from mayuri import Command, AddHandler, log_chat
from mayuri.modules.disableable import disableable
from mayuri.modules.helper.misc import EMOJI_PATTERN
from PIL import Image
from pyrogram import filters
from pyrogram.errors import PeerIdInvalid, StickersetInvalid, RPCError
from pyrogram.raw.functions.messages import GetStickerSet, SendMedia
from pyrogram.raw.functions.stickers import AddStickerToSet, CreateStickerSet
from pyrogram.raw.types import (
	DocumentAttributeFilename,
	InputDocument,
	InputMediaUploadedDocument,
	InputStickerSetItem,
	InputStickerSetShortName,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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

@disableable
async def kang_sticker(client, message):
	prog_msg = await message.reply_text("Memproses...")
	bot_username = (await client.get_me()).username
	sticker_emoji = "🤔"
	packnum = 0
	packname_found = False
	resize = False
	animated = False
	reply = message.reply_to_message
	user = await client.resolve_peer(message.from_user.username or message.from_user.id)
	if reply and reply.media:
		if reply.photo:
			resize = True
		elif reply.document:
			if "image" in reply.document.mime_type:
				# mime_type: image/webp
				resize = True
			elif "tgsticker" in reply.document.mime_type:
				# mime_type: application/x-tgsticker
				animated = True
		elif reply.sticker:
			if not reply.sticker.file_name:
				return await prog_msg.edit_text("Itu tidak dapat di Kang")
			if reply.sticker.emoji:
				sticker_emoji = reply.sticker.emoji
			animated = reply.sticker.is_animated
			if not reply.sticker.file_name.endswith(".tgs"):
				resize = True
		else:
			return await prog_msg.edit_text("Itu tidak dapat di Kang")
		pack_prefix = "anim" if animated else "c"
		packname = f"{pack_prefix}{message.from_user.id}_by_{bot_username}"

		if len(message.command) > 1:
			if message.command[1].isdigit() and int(message.command[1]) > 0:
				# provide pack number to kang in desired pack
				packnum = message.command.pop(1)
				packname = f"{pack_prefix}{packnum}_{message.from_user.id}_by_{bot_username}"
			if len(message.command) > 1:
				# matches all valid emojis in input
				sticker_emoji = (
					"".join(set(EMOJI_PATTERN.findall("".join(message.command[1:]))))
					or sticker_emoji
				)
		filename = await client.download_media(message.reply_to_message)
		if not filename:
			# Failed to download
			await prog_msg.delete()
			return
	elif message.entities and len(message.entities) > 1:
		packname = f"c{message.from_user.id}_by_{bot_username}"
		pack_prefix = "c"
		# searching if image_url is given
		img_url = None
		filename = "sticker.png"
		for y in message.entities:
			if y.type == "url":
				img_url = message.text[y.offset : (y.offset + y.length)]
				break
		if not img_url:
			await prog_msg.delete()
			return
		try:
			r = await http.get(img_url)
			if r.status_code == 200:
				with open(filename, mode="wb") as f:
					f.write(r.read())
		except Exception as r_e:
			return await prog_msg.edit_text(f"{r_e.__class__.__name__} : {r_e}")
		if len(message.command) > 2:
			# message.command[1] is image_url
			if message.command[2].isdigit() and int(message.command[2]) > 0:
				packnum = message.command.pop(2)
				packname = f"c{packnum}_{message.from_user.id}_by_{bot_username}"
			if len(message.command) > 2:
				sticker_emoji = (
					"".join(set(EMOJI_PATTERN.findall("".join(message.command[2:]))))
					or sticker_emoji
				)
			resize = True
	else:
		return await prog_msg.delete()

	try:
		if resize:
			filename = resize_image(filename)
		max_stickers = 50 if animated else 120
		while not packname_found:
			try:
				stickerset = await client.send(
					GetStickerSet(
						stickerset=InputStickerSetShortName(short_name=packname),
						hash=0
					)
				)
				if stickerset.set.count >= max_stickers:
					packnum += 1
					packname = (
						f"{pack_prefix}{packnum}_{message.from_user.id}_by_{bot_username}"
					)
				else:
					packname_found = True
			except StickersetInvalid:
				break
		file = await client.save_file(filename)
		media = await client.send(
			SendMedia(
				peer=(await client.resolve_peer(log_chat)),
				media=InputMediaUploadedDocument(
					file=file,
					mime_type=client.guess_mime_type(filename),
					attributes=[DocumentAttributeFilename(file_name=filename)],
				),
				message=f"#Sticker kang by UserID -> {message.from_user.id}",
				random_id=client.rnd_id(),
			)
		)
		stkr_file = media.updates[-1].message.media.document
		if packname_found:
			await client.send(
				AddStickerToSet(
					stickerset=InputStickerSetShortName(short_name=packname),
					sticker=InputStickerSetItem(
						document=InputDocument(
							id=stkr_file.id,
							access_hash=stkr_file.access_hash,
							file_reference=stkr_file.file_reference,
						),
						emoji=sticker_emoji,
					),
				)
			)
		else:
			await prog_msg.edit_text("Membuat Stickerpack...")
			u_name = message.from_user.username
			if u_name:
				u_name = f"@{u_name}"
			else:
				u_name = str(message.from_user.id)
			stkr_title = f"{u_name}'s "
			if animated:
				stkr_title += "Anim. "
			stkr_title += "MayuriPack"
			if packnum != 0:
				stkr_title += f" v{packnum}"
			try:
				await client.send(
					CreateStickerSet(
						user_id=user,
						title=stkr_title,
						short_name=packname,
						stickers=[
							InputStickerSetItem(
								document=InputDocument(
									id=stkr_file.id,
									access_hash=stkr_file.access_hash,
									file_reference=stkr_file.file_reference,
								),
								emoji=sticker_emoji,
							)
						],
						animated=animated,
					)
				)
			except PeerIdInvalid:
				return await prog_msg.edit_text(
					"Terjadi kesalahan saat membuat Stickerpack!",
					reply_markup=InlineKeyboardMarkup(
						[
							[
								InlineKeyboardButton(
									"/start", url=f"https://t.me/{bot_username}?start"
								)
							]
						]
					),
				)
	except Exception as all_e:
		await prog_msg.edit_text(f"{all_e.__class__.__name__} : {all_e}")
	else:
		markup = InlineKeyboardMarkup(
			[
				[
					InlineKeyboardButton(
						"Lihat Stickerpack",
						url=f"t.me/addstickers/{packname}",
					)
				]
			]
		)
		kanged_success_msg = "Sticker berhasil dikang"
		await prog_msg.edit_text(
			kanged_success_msg.format(sticker_emoji=sticker_emoji), reply_markup=markup
		)
		# Cleanup
		try:
			os.remove(filename)
		except OSError:
			pass

def resize_image(filename: str) -> str:
	im = Image.open(filename)
	maxsize = 512
	scale = maxsize / max(im.width, im.height)
	sizenew = (int(im.width * scale), int(im.height * scale))
	im = im.resize(sizenew, Image.NEAREST)
	downpath, f_name = os.path.split(filename)
	# not hardcoding png_image as "sticker.png"
	png_image = os.path.join(downpath, f"{f_name.split('.', 1)[0]}.png")
	im.save(png_image, "PNG")
	if png_image != filename:
		os.remove(filename)
	return png_image

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

AddHandler(stickerid,filters.command("stickerid", Command))
AddHandler(getsticker,filters.command("getsticker", Command))
AddHandler(kang_sticker,filters.command("kang", Command))
