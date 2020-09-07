import array

from functools import wraps

from mayuri import Command, OWNER, AddHandler, adminlist, admin
from mayuri.modules.disableable import disableable
from mayuri.modules.helper.string import split_quotes, parse_button, build_keyboard
from mayuri.modules.sql import filters as sql
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup

__MODULE__ = "Filters"
__HELP__ = """
Module ini digunakan untuk membuat reply otomatis untuk suatu kata.
[Filters]
> `/filter <kata> <balasan`
Menambahkan filter baru

> `/stop <kata>`
Menghapus filter

> `/filters`
Mendapatkan daftar filter aktif
"""

@admin
async def addfilter(client,message):
	chat_id = message.chat.id
	reply = message.reply_to_message
	text = (message.text).split(None, 1)
	filt_type = 0
	value = ""
	document = ""
	document_type = 0
	name = text[1].lower()
	extracted = split_quotes(name)
	if reply:
		if len(extracted) > 0:
			name = (extracted[0]).lower()
		else:
			await message.reply_text("Anda harus memberikan nama untuk filter ini!")
			return

		if reply.sticker:
			filt_type = 3
			document = reply.sticker.file_id
		elif reply.audio:
			filt_type = 4
			document_type = 1
			value = reply.caption
			document = reply.audio.file_id
		elif reply.document:
			filt_type = 4
			document_type = 2
			value = reply.caption
			document = reply.document.file_id
		elif reply.photo:
			filt_type = 4
			document_type = 3
			value = reply.caption
			document = reply.photo.file_id
		elif reply.video:
			filt_type = 4
			document_type = 4
			value = reply.caption
			document = reply.video.file_id
		else:
			filt_type = 1
			value = reply.text
			text, button = parse_button(value)
			text = text.strip()
			if not text:
				await message.reply_text("Anda harus menambahkan teks untuk filter ini, tidak bisa menggunakan button saja!")
				return
	else:
		if len(extracted) > 1:
			filt_type = 1
			name = extracted[0]
			value = extracted[1]
			text, button = parse_button(value)
			text = text.strip()
			if not text:
				await message.reply_text("Anda harus menambahkan teks untuk filter ini, tidak bisa menggunakan button saja!")
				return
		else:
			await message.reply_text("Anda harus memberikan reply untuk filter ini!")
			return
	sql.add_to_filter(chat_id,name,value,document,filt_type,document_type)
	await message.reply_text("Handler <code>{}</code> Telah ditambahkan di {}".format(name,message.chat.title),disable_web_page_preview=True)


@admin
async def rm_filter(client,message):
	chat_id = message.chat.id
	admin_list = await adminlist(client,chat_id)
	text = (message.text).split(None, 1)
	if len(text) > 1:
		name = text[1]
		extracted = split_quotes(name)
		if len(extracted) > 0:
			name = extracted[0].lower()

		if sql.rm_from_filter(chat_id,name):
			await message.reply_text("Saya akan berhenti membalas <code>{}</code> di {}!".format(name,message.chat.title),disable_web_page_preview=True)
		else:
			await message.reply_text("<code>{}</code> Bukan filter aktif!".format(name),disable_web_page_preview=True)
	else:
		await message.reply_text("Apa yang mau dihapus dari filter?")

def name(func):
	wraps(func)
	@disableable
	async def filters(client,message):
		return await func(client,message)
	return filters

@name
async def filters_list(client,message):
	chat_id = message.chat.id
	list_name = sql.filter_list(chat_id)
	text = "Daftar filters di Grup ini:\n"
	if list_name:
		for name in list_name:
			text = text+" - <code>{}</code>\n".format(name.name)
		await message.reply_text(text,disable_web_page_preview=True)
	else:
		await message.reply_text("Tidak ada filters di {}!".format(message.chat.title))

async def filtr(client,message):
	chat_id = message.chat.id
	text = (message.text).lower()
	text = text.split()
	data_list = []
	mode_list = []
	check = sql.filter_list(chat_id)
	if not check:
		return

	for filt in check:
		if filt.name in text:
			value = filt.value
			text, button = parse_button(value)
			button = build_keyboard(button)
			if button:
				button = InlineKeyboardMarkup(button)
			else:
				button = None

			if filt.filter_type == 1:
				await message.reply_text(text,reply_markup=button)
			elif filt.filter_type == 3:
				await message.reply_sticker(filt.document)
			elif filt.filter_type == 4:
				if filt.document_type == 1:
					await message.reply_audio(audio=filt.document,caption=text,reply_markup=button)
				elif filt.document_type == 2:
					await message.reply_document(document=filt.document,caption=text,reply_markup=button)
				elif filt.document_type == 3:
					await message.reply_photo(photo=filt.document,caption=text,reply_markup=button)
				elif filt.document_type == 3:
					await message.reply_video(video=filt.document,caption=text,reply_markup=button)
			break

AddHandler(addfilter,filters.command("filter", Command) & filters.group)
AddHandler(rm_filter,filters.command("stop", Command) & filters.group)
AddHandler(filters_list,filters.command("filters", Command) & filters.group)
