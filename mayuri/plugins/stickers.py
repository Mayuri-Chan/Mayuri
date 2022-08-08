import os
from mayuri import PREFIX
from mayuri.mayuri import Mayuri
from mayuri.utils.lang import tl
from pyrogram import filters

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
