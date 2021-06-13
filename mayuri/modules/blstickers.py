import array

from mayuri import Command, OWNER, AddHandler, adminlist, admin
from mayuri.modules.disableable import disableable
from mayuri.modules.helper.time import create_time
from mayuri.modules.helper.string import split_quotes
from mayuri.modules.sql import blstickers as sql
from pyrogram import filters
from pyrogram.types import ChatPermissions
from time import time

__MODULE__ = "Stickers Blacklist"
__HELP__ = """
Module ini digunakan untuk melarang penggunaan suatu sticker.

[Sticker Blacklist]
reply ke sticker yang akan di blacklist
> `/addbl [<mode>] [<waktu>]`
Menambahkan kata kedalam daftar hitam
contoh :
> `/addbl`
> `/addbl kick`
> `/addbl tmute 12h`

> `/rmbl`
Menghapus sticker dari daftar hitam

> `/blacklist`
Menampilkan daftar sticker yang ada di daftar hitam

[Mode]
Opsional, mode defaultnya adalah delete
- delete	- ban
- kick		- tmute
- mute		- tban


[Waktu]
Khusus mode tmute dan tban
daftar unit waktu :
- s = detik
- m = menit
- h = jam
- d = hari
"""

@admin
async def addbl(client,message):
	chat_id = message.chat.id
	mode_list = {'delete': 0,'tmute': 1,'mute': 2,'kick': 3,'tban': 4,'ban': 5}
	unit_list = ['d','h','m','s']
	if message.reply_to_message:
		sticker = message.reply_to_message.sticker
		stickerid = sticker.file_unique_id
		args = message.text.split(None,1)
		if len(args) > 1:
			mode_raw = args[1].lower();
		else:
			mode_raw = "delete"
	else:
		text = (message.text).split(None, 1)
		stickerid = text[1]
		extracted = split_quotes(stickerid)

		if len(extracted) > 0:
			stickerid = extracted[0]
			if len(extracted) < 2:
				mode_raw = "delete"
			else:
				mode_raw = extracted[1].lower()
				if mode_raw not in mode_list:
					mode_raw = ((extracted[1]).split())[0]
		else:
			mode_raw = text[2]

	mode = mode_list[mode_raw]

	if mode == 0 or mode == 2 or mode == 3 or mode == 5:
		time = 0
		mode_text = "mode {}".format(mode_raw)
	else:
		if len(extracted) > 0:
			time = (extracted[1]).split()
			if len(time) < 2:
				await message.reply_text("Anda memasukan durasi untuk menggunakan mode {}".format(mode_raw))
				return

			time = time[1]
		else:
			time = text[3]


		unit = time[-1]
		if unit not in unit_list:
			message.reply_text("Format durasi yang anda masukkan salah")
			return
		else:
			mode_text = "mode {} dan durasi selama {}".format(mode_raw,time)

	sql.add_to_blstickers(chat_id,stickerid,mode,time)
	await message.reply_text("Sticker <code>{}</code> Telah ditambahkan ke Blacklist dengan {}".format(stickerid,mode_text),disable_web_page_preview=True)

@admin
async def rm_bl(client,message):
	chat_id = message.chat.id
	if message.reply_to_message:
		sticker = message.reply_to_message.sticker
		stickerid = sticker.file_unique_id
	elif message.text:
		text = (message.text).split(None, 1)
		stickerid = text[1]
		extracted = split_quotes(stickerid)
	else:
		await message.reply_text("Sticker mana yang dihapus dari daftar hitam?")

	if sql.rm_from_blstickers(chat_id,stickerid):
		await message.reply_text("Sticker <code>{}</code> Berhasil dihapus dari Blacklist!".format(stickerid),disable_web_page_preview=True)
	else:
		await message.reply_text("Sticker <code>{}</code> Gagal dihapus dari Blacklist!".format(stickerid),disable_web_page_preview=True)

@disableable
async def blacklist(client,message):
	chat_id = message.chat.id
	list_stickerid = sql.blstickers_list(chat_id)
	delete = []
	mute = []
	kick = []
	ban = []
	tmute = []
	tban = []
	tmute_time = []
	tban_time = []
	if list_stickerid:
		for stickerid in list_stickerid:
			if stickerid.mode == 0:
				delete.append(stickerid.stickerid)
			elif stickerid.mode == 1:
				tmute.append(stickerid.stickerid)
				tmute_time.append(stickerid.time)
			elif stickerid.mode == 2:
				mute.append(stickerid.stickerid)
			elif stickerid.mode == 3:
				kick.append(stickerid.stickerid)
			elif stickerid.mode == 4:
				tban.append(stickerid.stickerid)
				tban_time.append(stickerid.time)
			elif stickerid.mode == 5:
				ban.append(stickerid.stickerid)
		text = "Daftar sticker yang diblacklist di Grup ini:\n"
		if len(delete) > 0:
			text = text+"\nDelete :\n"
			for x in delete:
				text = text+" - <code>{}</code>\n".format(x)
		if len(mute) > 0:
			text = text+"\nMute :\n"
			for x in mute:
				text = text+" - <code>{}</code>\n".format(x)
		if len(kick) > 0:
			text = text+"\nKick :\n"
			for x in kick:
				text = text+" - <code>{}</code>\n".format(x)
		if len(ban) > 0:
			text = text+"\nBan :\n"
			for x in ban:
				text = text+" - <code>{}</code>\n".format(x)
		if len(tmute) > 0:
			text = text+"\nTemp Mute :\n"
			i = 0
			for x in tmute:
				text = text+" - <code>{}</code> ({})\n".format(x,tmute_time[i])
				i = i+1
		if len(tban) > 0:
			text = text+"\nTemp Ban :\n"
			i = 0
			for x in tban:
				text = text+" - <code>{}</code> ({})\n".format(x,tban_time[i])
				i = i+1

		await message.reply_text(text,disable_web_page_preview=True)

	else:
		await message.reply_text("Tidak ada kata yang diblacklist di Grup ini!")

async def blsticker(client,message):
	#log_id = 
	chat_id = message.chat.id
	user_id = message.from_user.id
	mention = message.from_user.mention
	chat_title = message.chat.title
	admin_list = await adminlist(client,chat_id)
	sticker = message.sticker.file_unique_id
	data_list = []
	mode_list = []
	if (user_id not in admin_list) and (user_id not in OWNER):
		check = sql.blstickers_list(chat_id)
		if not check:
			return

		for stickerid in check:
			if sticker in stickerid.stickerid:
				time_raw = stickerid.time
				time = create_time(time_raw)
				if stickerid.mode == 0:
					data_list.append({'stickerid': stickerid.stickerid,'mode': stickerid.mode})
					if stickerid.mode not in mode_list:
						mode_list.append(stickerid.mode)
				elif stickerid.mode == 1:
					data_list.append({'stickerid': stickerid.stickerid,'mode': stickerid.mode})
					if stickerid.mode not in mode_list:
						mode_list.append(stickerid.mode)
				elif stickerid.mode == 2:
					data_list.append({'stickerid': stickerid.stickerid,'mode': stickerid.mode})
					if stickerid.mode not in mode_list:
						mode_list.append(stickerid.mode)
				elif stickerid.mode == 3:
					data_list.append({'stickerid': stickerid.stickerid,'mode': stickerid.mode})
					if stickerid.mode not in mode_list:
						mode_list.append(stickerid.mode)
				elif stickerid.mode == 4:
					data_list.append({'stickerid': stickerid.stickerid,'mode': stickerid.mode})
					if stickerid.mode not in mode_list:
						mode_list.append(stickerid.mode)
				elif stickerid.mode == 5:
					data_list.append({'stickerid': stickerid.stickerid,'mode': stickerid.mode})
					if stickerid.mode not in mode_list:
						mode_list.append(stickerid.mode)

		mode_list.sort()
		if len(mode_list) > 1:
			mode = mode_list[len(mode_list)-1]
			for data in data_list:
				if data["mode"] == mode:
					stickerid = data["stickerid"]
					break

		elif len(mode_list) == 1:
			mode = mode_list[0]
			stickerid = data_list[0]["stickerid"]
		else:
			return

		if mode == 0:
			await message.delete()
			#await client.send_message(log_id,"#BLACKLIST_DELETE\n{}\nUser : {}\nAlasan : Mengirimkan sticker <code>{}</code>".format(chat_title,mention,stickerid))
		elif mode == 1:
			await message.delete()
			await client.restrict_chat_member(chat_id, user_id, ChatPermissions(), time)
			await message.reply_text("Dibisukan untuk {}\nUser : {}\nAlasan : Mengirimkan sticker <code>{}</code>".format(time_raw,mention,stickerid),disable_web_page_preview=True)
			#await client.send_message(log_id,"#BLACKLIST_TMUTE\n{}\nUser : {}\nDurasi : {}\nAlasan : Mengirimkan sticker <code>{}</code>".format(chat_title,mention,time_raw,stickerid))
		elif mode == 2:
			await message.delete()
			await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
			await message.reply_text("Dibisukan!\nUser : {}\nAlasan : Mengirimkan sticker <code>{}</code>".format(mention,stickerid),disable_web_page_preview=True)
			#await client.send_message(log_id,"#BLACKLIST_MUTE\n{}\nUser : {}\nAlasan : Mengirimkan sticker <code>{}</code>".format(chat_title,mention,stickerid))
		elif mode == 3:
			await message.delete()
			await client.kick_chat_member(chat_id,user_id)
			await client.unban_chat_member(chat_id,user_id)
			await message.reply_sticker("https://t.me/CactusID_OOT/116113")
			await message.reply_text("Ditendang! 😝\nUser : {}\nAlasan : Mengirimkan Sticker <code>{}</code>".format(mention,stickerid),disable_web_page_preview=True)
			#await client.send_message(log_id,"#BLACKLIST_KICK\n{}\nUser : {}\nAlasan : Mengirimkan sticker <code>{}</code>".format(chat_title,mention,stickerid))
		elif mode == 4:
			await message.delete()
			await client.kick_chat_member(chat_id,user_id, time)
			await message.reply_sticker("https://t.me/CactusID_OOT/116113")
			await message.reply_text("Terbanned untuk {}! 😝\nUser : {}\nAlasan : Mengirimkan Sticker <code>{}</code>".format(time_raw,mention,stickerid),disable_web_page_preview=True)
			#await client.send_message(log_id,"#BLACKLIST_TBAN\n{}\nUser : {}\nDurasi : {}\nAlasan : Mengirimkan sticker <code>{}</code>".format(chat_title,mention,time_raw,stickerid))
		elif mode == 5:
			await message.delete()
			await client.kick_chat_member(chat_id,user_id)
			await message.reply_sticker("https://t.me/CactusID_OOT/116113")
			await message.reply_text("Terbanned! 😝\nUser : {}\nAlasan : Mengirimkan Sticker <code>{}</code>".format(mention,stickerid),disable_web_page_preview=True)
			#await client.send_message(log_id,"#BLACKLIST_BAN\n{}\nUser : {}\nAlasan : Mengirimkan sticker <code>{}</code>".format(chat_title,mention,stickerid))

AddHandler(addbl,filters.command("addblsticker", Command) & filters.group)
AddHandler(rm_bl,filters.command("rmblsticker", Command) & filters.group)
AddHandler(blacklist,filters.command("blsticker", Command) & filters.group)
