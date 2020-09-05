import array

from functools import wraps

from mayuri import bot, Command, AddHandler, DisableAbleLs, adminlist, admin
from mayuri.modules.helper.string import after
from mayuri.modules.sql import disableable as sql
from pyrogram import filters
from pyrogram.handlers import MessageHandler

__MODULE__ = "Disable Commands"
__HELP__ = """
Modul ini digunakan untuk menon-aftikan penggunaan perintah didalam grup
[Disable Commands]
> `/disable <perintah>`
Untuk menonaktifkan perintah
contoh :
> `/disable adminlist`

> `/enable <perintah>`
Untuk mengaktifkan kembali perintah yang telah di non-aktifkan
contoh :
> `/enable adminlist`

> `/disabled`
Untuk menampilkan daftar perintah yang telah di non-aktifkan

> `/disableable`
Untuk menampilkan daftar perintah yang dapat di non-aktifkan
"""

def disableable(func):
	wraps(func)
	name = func.__name__
	if name not in DisableAbleLs:
		DisableAbleLs.append(name)

	async def decorator(client,message):
		chat_id = message.chat.id
		if not sql.check_disableable(chat_id,name):
			await func(client,message)

	return decorator

@admin
async def disablehandler(client,message):
	chat_id = message.chat.id
	text = (message.text).split()
	if len(text) < 2:
		await message.reply_text("Apa yang mau didisable!")
	else:
		command = text[1]
		if command not in DisableAbleLs:
			await message.reply_text("Perintah tidak dapat didisable!")
		else:
			sql.add_to_disableable(chat_id,command)
			await message.reply_text("Perintah berhasil didisable!")

@admin
async def enablehandler(client,message):
	chat_id = message.chat.id
	text = (message.text).split()
	if len(text) > 1:
		command = text[1]
		if sql.rm_from_disableable(chat_id,command):
			await message.reply_text("Command {} Berhasil dienable!".format(command))
		else:
			await message.reply_text("Command {} Gagal dienable!".format(command))
	else:
		await message.reply_text("Command Apa yang mau dienable?")

async def disabled_list(client,message):
	chat_id = message.chat.id
	list_disabled = sql.get_disabled(chat_id)
	if list_disabled:
		text = "Daftar Perintah yang didisable di grup ini:"
		for disabled in list_disabled:
			text = text+"\n - {}".format(disabled.command)

		await message.reply_text(text)
	else:
		await message.reply_text("Tidak ada Perintah yang didisable di grup ini!")

async def disableable_list(client,message):
	if message.chat.type == 'group' or message.chat.type == 'supergroup':
		chat_id = message.chat.id
		admin_list = await adminlist(client,chat_id)
		if message.from_user.id not in admin_list:
			return

	DisableAbleLs.sort()
	text = "Daftar Perintah yang dapat didisable:"
	for disableable in DisableAbleLs:
		text = text+"\n - {}".format(disableable)

	await message.reply_text(text)

AddHandler(disablehandler,filters.group & filters.command("disable", Command))
AddHandler(enablehandler,filters.group & filters.command("enable", Command))
AddHandler(disabled_list,filters.group & filters.command("disabled", Command))
AddHandler(disableable_list,filters.command("disableable", Command))