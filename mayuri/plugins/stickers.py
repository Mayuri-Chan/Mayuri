import cv2
import os
import re
from mayuri import PREFIX
from mayuri.mayuri import Mayuri
from mayuri.util.filters import disable
from pyrogram import enums, filters

__PLUGIN__ = "stickers"
__HELP__ = "stickers_help"

@Mayuri.on_message(filters.command("stickerid", PREFIX))
@disable
async def cmd_stickerid(c,m):
	chat_id = m.chat.id
	if m.reply_to_message and m.reply_to_message.sticker:
		await m.reply_text((await c.tl(chat_id, "your_stickerid")).format(m.reply_to_message.sticker.file_id))
	else:
		await m.reply_text(await c.tl(chat_id, "must_reply_to_sticker"))

@Mayuri.on_message(filters.command("getsticker", PREFIX))
@disable
async def cmd_getsticker(c,m):
	chat_id = m.chat.id
	animated = False
	videos = False
	if m.reply_to_message and m.reply_to_message.sticker:
		file = m.reply_to_message.sticker
		animated = m.reply_to_message.sticker.is_animated
		videos = m.reply_to_message.sticker.is_video
		filename = "images/"
		filename += "sticker.tgs" if animated else ("sticker.webm" if videos else "sticker.png")
		await m.reply_text(await c.tl(chat_id, "use_whisely"))
		await c.download_media(file, file_name=filename)
		filename = "mayuri/" + filename
		thread_id = None
		if m.message_thread_id:
			thread_id = m.message_thread_id
		if animated:
			await m.reply_text(await c.tl(chat_id, "animated_not_supported"))
		elif videos:
			await c.send_chat_action(m.chat.id, enums.ChatAction.UPLOAD_VIDEO, message_thread_id=thread_id)
			await m.reply_video(video=open(filename, 'rb'))
			await m.reply_document(document=open(filename, 'rb'), force_document=True)
		else:
			await c.send_chat_action(m.chat.id, enums.ChatAction.UPLOAD_PHOTO, message_thread_id=thread_id)
			await m.reply_photo(photo=open(filename, 'rb'))
			await c.send_chat_action(m.chat.id, enums.ChatAction.UPLOAD_DOCUMENT, message_thread_id=thread_id)
			await m.reply_document(document=open(filename, 'rb'), force_document=True)
		os.remove(filename)
	else:
		await m.reply_text(await c.tl(chat_id, "must_reply_to_sticker"))
