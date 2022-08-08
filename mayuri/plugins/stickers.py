import cv2
import os
from mayuri import LOG_CHAT, PREFIX
from mayuri.mayuri import Mayuri
from mayuri.utils.lang import tl
from mayuri.utils.misc import EMOJI_PATTERN, http
from pyrogram import filters
from pyrogram.errors import PeerIdInvalid, StickersetInvalid
from pyrogram.raw.functions.messages import GetStickerSet, SendMedia
from pyrogram.raw.functions.stickers import AddStickerToSet, CreateStickerSet
from pyrogram.raw.types import (
	DocumentAttributeFilename,
	InputDocument,
	InputMediaUploadedDocument,
	InputStickerSetItem,
	InputStickerSetShortName,
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

__PLUGIN__ = "stickers"
__HELP__ = "stickers_help"

@Mayuri.on_message(filters.command("stickerid", PREFIX))
async def stickerid(c,m):
	chat_id = m.chat.id
	if m.reply_to_message and m.reply_to_message.sticker:
		await m.reply_text((await tl(chat_id, "your_stickerid")).format(m.reply_to_message.sticker.file_id))
	else:
		await m.reply_text(await tl(chat_id, "must_reply_to_sticker"))

@Mayuri.on_message(filters.command("getsticker", PREFIX))
async def getsticker(c,m):
	chat_id = m.chat.id
	animated = False
	videos = False
	if m.reply_to_message and m.reply_to_message.sticker:
		file = m.reply_to_message.sticker
		animated = m.reply_to_message.sticker.is_animated
		videos = m.reply_to_message.sticker.is_video
		filename = "images/"
		filename += "sticker.tgs" if animated else ("sticker.webm" if videos else "sticker.png")
		await m.reply_text(await tl(chat_id, "use_whisely"))
		await c.download_media(file, file_name=filename)
		filename = "mayuri/" + filename
		if animated:
			await m.reply_text(await tl(chat_id, "animated_not_supported"))
		elif videos:
			await m.reply_video(video=open(filename, 'rb'))
			await m.reply_document(document=open(filename, 'rb'), force_document=True)
		else:
			await m.reply_photo(photo=open(filename, 'rb'))
			await m.reply_document(document=open(filename, 'rb'), force_document=True)
		os.remove(filename)
	else:
		await m.reply_text(await tl(chat_id, "must_reply_to_sticker"))

@Mayuri.on_message(filters.command("kang", PREFIX))
async def kang_sticker(c, m):
	chat_id = m.chat.id
	prog_msg = await m.reply_text(await tl(chat_id, "processing"))
	bot_username = (await c.get_me()).username
	sticker_emoji = "🤔"
	packnum = 0
	packname_found = False
	resize = False
	animated = False
	videos = False
	reply = m.reply_to_message
	user = await c.resolve_peer(m.from_user.username or m.from_user.id)
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
			elif "video/webm" in reply.document.mime_type:
				videos = True
		elif reply.sticker:
			if not reply.sticker.file_name:
				return await prog_msg.edit_text(await tl(chat_id, "cannot_kang"))
			if reply.sticker.emoji:
				sticker_emoji = reply.sticker.emoji
			animated = reply.sticker.is_animated
			videos = reply.sticker.is_video
			if not reply.sticker.file_name.endswith(".tgs") and not reply.sticker.file_name.endswith(".webm"):
				resize = True
		else:
			return await prog_msg.edit_text(await tl(chat_id, "cannot_kang"))
		pack_prefix = "anim" if animated else ("vid" if videos else "c")
		packname = f"{pack_prefix}{m.from_user.id}_by_{bot_username}"

		if len(m.command) > 1:
			if m.command[1].isdigit() and int(m.command[1]) > 0:
				# provide pack number to kang in desired pack
				packnum = m.command.pop(1)
				packname = f"{pack_prefix}{packnum}_{m.from_user.id}_by_{bot_username}"
			if len(m.command) > 1:
				# matches all valid emojis in input
				sticker_emoji = (
					"".join(set(EMOJI_PATTERN.findall("".join(m.command[1:]))))
					or sticker_emoji
				)
		filename = await c.download_media(m.reply_to_message)
		if not filename:
			# Failed to download
			await prog_msg.delete()
			return
	elif m.entities and len(m.entities) > 1:
		packname = f"c{m.from_user.id}_by_{bot_username}"
		pack_prefix = "a"
		# searching if image_url is given
		img_url = None
		filename = "sticker.png"
		for y in m.entities:
			if y.type == "url":
				img_url = m.text[y.offset : (y.offset + y.length)]
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
		if len(m.command) > 2:
			# m.command[1] is image_url
			if m.command[2].isdigit() and int(m.command[2]) > 0:
				packnum = m.command.pop(2)
				packname = f"c{packnum}_{m.from_user.id}_by_{bot_username}"
			if len(m.command) > 2:
				sticker_emoji = (
					"".join(set(EMOJI_PATTERN.findall("".join(m.command[2:]))))
					or sticker_emoji
				)
			resize = True
	else:
		return await prog_msg.delete()

	try:
		if resize:
			filename = resize_image(filename)
		max_stickers = 50 if animated else (50 if videos else 120)
		while not packname_found:
			try:
				stickerset = await c.invoke(
					GetStickerSet(
						stickerset=InputStickerSetShortName(short_name=packname),
						hash=0
					)
				)
				if stickerset.set.count >= max_stickers:
					packnum += 1
					packname = (
						f"{pack_prefix}{packnum}_{m.from_user.id}_by_{bot_username}"
					)
				else:
					packname_found = True
			except StickersetInvalid:
				break
		file = await c.save_file(filename)
		media = await c.invoke(
			SendMedia(
				peer=(await c.resolve_peer(LOG_CHAT)),
				media=InputMediaUploadedDocument(
					file=file,
					mime_type=c.guess_mime_type(filename),
					attributes=[DocumentAttributeFilename(file_name=filename)],
				),
				message=f"#Sticker kang by UserID -> {m.from_user.id}",
				random_id=c.rnd_id(),
			)
		)
		stkr_file = media.updates[-1].message.media.document
		if packname_found:
			await c.invoke(
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
			await prog_msg.edit_text(await tl(chat_id, "creating_pack"))
			u_name = m.from_user.username
			if u_name:
				u_name = f"@{u_name}"
			else:
				u_name = str(m.from_user.id)
			stkr_title = f"{u_name}'s "
			if animated:
				stkr_title += "Anim. "
			if videos:
				stkr_title += "Vid. "
			stkr_title += "MayuriPack"
			if packnum != 0:
				stkr_title += f" v{packnum}"
			try:
				await c.invoke(
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
						videos=videos,
					)
				)
			except PeerIdInvalid:
				return await prog_msg.edit_text(
					await tl(chat_id, "cannot_create_pack"),
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
						await tl(chat_id, "show_pack"),
						url=f"t.me/addstickers/{packname}",
					)
				]
			]
		)
		kanged_success_msg = await tl(chat_id, "sticker_kanged")
		await prog_msg.edit_text(
			kanged_success_msg.format(sticker_emoji=sticker_emoji), reply_markup=markup
		)
		# Cleanup
		try:
			os.remove(filename)
		except OSError:
			pass

def resize_image(filename: str) -> str:
	im = cv2.imread(filename)
	maxsize = 512
	width = int(im.shape[1])
	height = int(im.shape[0])
	scale = maxsize / max(width, height)
	sizenew = (int(width * scale), int(height * scale))
	im = cv2.resize(im, sizenew, interpolation=cv2.INTER_NEAREST)
	downpath, f_name = os.path.split(filename)
	# not hardcoding png_image as "sticker.png"
	png_image = os.path.join(downpath, f"{f_name.split('.', 1)[0]}.png")
	cv2.imwrite(png_image, im)
	if png_image != filename:
		os.remove(filename)
	return png_image
