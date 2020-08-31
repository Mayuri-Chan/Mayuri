import array

from mayuri import bot, Command, OWNER
from mayuri.modules.helper.misc import adminlist
from mayuri.modules.helper.time import create_time
from mayuri.modules.helper.string import after, between
from mayuri.modules.sql import anti_ubot as sql
from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import ChatPermissions
from time import time

@bot.on_message(filters.command("addblubot", Command) & filters.group)
async def addblubot(client,message):
	chat_id = message.chat.id
	admin_list = await adminlist(client,chat_id)
	if message.from_user.id not in admin_list:
		return

	mode_list = {'mute': 1,'kick': 2,'ban': 3,'tmute': 4,'tban': 5}
	unit_list = ['d','h','m','s']
	text = (message.text).split()
	if len(text) < 3:
		await message.reply_text("Format yang anda masukkan salah")
		return

	command = text[1]
	mode_raw = text[2]
	mode = mode_list[mode_raw]
	if mode == 1 or mode == 2 or mode == 3:
		time = 0
		mode_text = "mode {}".format(mode_raw)
	else:
		if len(text) < 4:
			message.reply_text("Anda memasukan durasi untuk menggunakan mode {}".format(text[2]))
			return

		time = text[3]
		unit = time[-1]
		if unit not in unit_list:
			message.reply_text("Format durasi yang anda masukkan salah")
			return
		else:
			mode_text = "mode {} dan durasi selama {}".format(mode_raw,time)

	sql.add_to_antiubot(chat_id,command,mode,time)
	await message.reply_text("Command {} Telah ditambahkan ke Blacklist dengan {}".format(command,mode_text))

@bot.on_message(filters.command("rmblubot", Command) & filters.group)
async def rm_blubot(client,message):
	chat_id = message.chat.id
	admin_list = await adminlist(client,chat_id)
	if message.from_user.id not in admin_list:
		return

	text = (message.text).split()
	if len(text) > 1:
		command = text[1]
		if sql.rm_from_antiubot(chat_id,command):
			await message.reply_text("Command {} Berhasil dihapus dari Blacklist Userbot!".format(command))
		else:
			await message.reply_text("Command {} Gagal dihapus dari Blacklist Userbot!".format(command))
	else:
		await message.reply_text("Command Apa yang mau dihapus dari Blacklist Userbot?")

@bot.on_message(filters.command("blubot", Command) & filters.group)
async def blbot_list(client,message):
	chat_id = message.chat.id
	list_command = sql.antiubot_list(chat_id)
	mute = []
	kick = []
	ban = []
	tmute = []
	tban = []
	tmute_time = []
	tban_time = []
	if list_command:
		for command in list_command:
			if command.mode == 1:
				mute.append(command.command)
			elif command.mode == 2:
				kick.append(command.command)
			elif command.mode == 3:
				ban.append(command.command)
			elif command.mode == 4:
				tmute.append(command.command)
				tmute_time.append(command.time)
			elif command.mode == 5:
				tban.append(command.command)
				tban_time.append(command.time)
		text = "Daftar Command Userbot yang diblacklist di Grup ini:\n"
		if len(mute) > 0:
			text = text+"\nMute :\n"
			for x in mute:
				text = text+" - {}\n".format(x)
		if len(kick) > 0:
			text = text+"\nKick :\n"
			for x in kick:
				text = text+" - {}\n".format(x)
		if len(ban) > 0:
			text = text+"\nBan :\n"
			for x in ban:
				text = text+" - {}\n".format(x)
		if len(tmute) > 0:
			text = text+"\nTemp Mute :\n"
			i = 0
			for x in tmute:
				text = text+" - {} ({})\n".format(x,tmute_time[i])
				i = i+1
		if len(tban) > 0:
			text = text+"\nTemp Ban :\n"
			i = 0
			for x in tban:
				text = text+" - {} ({})\n".format(x,tban_time[i])
				i = i+1

		await message.reply_text(text)

	else:
		await message.reply_text("Tidak ada Command Userbot yang diblacklist di Grup ini!")

@bot.on_message(filters.text & filters.group)
async def bl_ubot(client,message):
	unsafe_pattern = r'^[^/!#@\$A-Za-z]'
	#log_id = 
	chat_id = message.chat.id
	user_id = message.from_user.id
	mention = message.from_user.mention
	chat_title = message.chat.title
	admin_list = await adminlist(client,chat_id)
	text = message.text
	first = text[0]
	if ' ' in text:
		command = between(text,first,' ')
	else:
		command = after(text,first)
	if (user_id not in admin_list) and (user_id not in OWNER):
		if first not in unsafe_pattern:
			check = sql.check_antiubot(chat_id,command)
			if not check:
				return
			time_raw = check.time
			time = create_time(time_raw)
			if check.mode == 1:
				await message.delete()
				await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
				await message.reply_text("Dibisukan!\nUser : {}\nAlasan : Mengatakan {}{}".format(mention,first,command))
				#await client.send_message(log_id,"#UBOT_MUTE\n{}\nUser : {}\nAlasan : Mengatakan {}{}".format(chat_title,mention,first,command))
			elif check.mode == 2:
				await message.delete()
				await client.kick_chat_member(chat_id,user_id)
				await client.unban_chat_member(chat_id,user_id)
				await message.reply_sticker("https://t.me/CactusID_OOT/116113")
				await message.reply_text("Ditendang! 😝\nUser : {}\nAlasan : Mengatakan {}{}".format(mention,first,command))
				#await client.send_message(log_id,"#UBOT_TENDANG\n{}\nUser : {}\nAlasan : Mengatakan {}{}".format(chat_title,mention,first,command))
			elif check.mode == 3:
				await message.delete()
				await client.kick_chat_member(chat_id,user_id)
				await message.reply_sticker("https://t.me/CactusID_OOT/116113")
				await message.reply_text("Terbanned! 😝\nUser : {}\nAlasan : Mengatakan {}{}".format(mention,first,command))
				#await client.send_message(log_id,"#UBOT_BAN\n{}\nUser : {}\nAlasan : Mengatakan {}{}".format(chat_title,mention,first,command))
			elif check.mode == 4:
				await message.delete()
				await client.restrict_chat_member(chat_id, user_id, ChatPermissions(), time)
				await message.reply_text("Dibisukan untuk {}\nUser : {}\nAlasan : Mengatakan {}{}".format(time_raw,mention,first,command))
				#await client.send_message(log_id,"#UBOT_TMUTE\n{}\nUser : {}\nDurasi : {}\nAlasan : Mengatakan {}{}".format(chat_title,mention,time_raw,first,command))
			elif check.mode == 5:
				await message.delete()
				await client.kick_chat_member(chat_id,user_id, time)
				await message.reply_sticker("https://t.me/CactusID_OOT/116113")
				await message.reply_text("Terbanned untuk {}! 😝\nUser : {}\nAlasan : Mengatakan {}{}".format(time_raw,mention,first,command))
				#await client.send_message(log_id,"#UBOT_TBAN\n{}\nUser : {}\nDurasi : {}\nAlasan : Mengatakan {}{}".format(chat_title,mention,time_raw,first,command))

