import array

from mayuri import bot, Command, OWNER, AddHandler, DisableAbleLs
from mayuri.modules.helper.misc import adminlist
from mayuri.modules.helper.string import after
from mayuri.modules.sql import disableable as sql
from pyrogram import filters
from pyrogram.handlers import MessageHandler

def DisableAbleHandler(func,filt,name):
	if name not in DisableAbleLs:
		DisableAbleLs.append(name)

	my_handler = MessageHandler(func,filt)
	bot.add_handler(my_handler)

def CheckDisable(chat_id,command):
	command = str(command)
	if ' ' in command:
		command = command.split()
		if '$' in command:
			command = after(command[0],'$')
		else:
			command = after(command[0],'/')
	else:
		if '$' in command:
			command = after(command,'$')
		else:
			command = after(command,'/')

	return sql.check_disableable(chat_id,command)

async def disablehandler(client,message):
	chat_id = message.chat.id
	admin_list = await adminlist(client,chat_id)
	if message.from_user.id not in admin_list:
		return
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

async def enablehandler(client,message):
	chat_id = message.chat.id
	admin_list = await adminlist(client,chat_id)
	if message.from_user.id not in admin_list:
		return

	text = (message.text).split()
	if len(text) > 1:
		command = text[1]
		if sql.rm_from_disableable(chat_id,command):
			await message.reply_text("Command {} Berhasil dienable!".format(command))
		else:
			await message.reply_text("Command {} Gagal dienable!".format(command))
	else:
		await message.reply_text("Command Apa yang mau dienable?")

AddHandler(disablehandler,filters.group & filters.command("disable", Command))
AddHandler(enablehandler,filters.group & filters.command("enable", Command))