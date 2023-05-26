import re

from datetime import datetime
from mayuri import PREFIX
from mayuri.mayuri import Mayuri
from mayuri.util.filters import admin_only, disable
from mayuri.util.string import split_quotes
from mayuri.util.time import create_time, tl_time
from pyrogram import filters
from pyrogram.types import ChatPermissions

__PLUGIN__ = "blsticker"
__HELP__ = "blsticker_help"

@Mayuri.on_message(filters.command("addblsticker", PREFIX) & admin_only)
async def addblsticker(c,m):
	db = c.db["blacklist_sticker"]
	chat_id = m.chat.id
	mode_list = {'delete': 0,'mute': 1, 'kick': 2,'ban': 3}
	duration = ""
	reason = ""
	if m.reply_to_message:
		sticker = m.reply_to_message.sticker
		stickerid = sticker.file_unique_id
		text = m.text
		text = text.split(None, 1)
		if len(text) > 1:
			extracted = split_quotes(text[1])
			mode_raw = extracted[0]
			if len(extracted) > 1:
				if re.match(r"([0-9]{1,})([dhms])$", text[1].lower()):
					duration = text[1]
					if len(extracted) > 2:
						reason = extracted[2]
				else:
					extracted1 = split_quotes(extracted[1])
					if re.match(r"([0-9]{1,})([dhms])$", extracted1[0].lower()):
						duration = extracted1[0]
						if len(extracted1) > 1:
							reason = extracted1[1]
					else:
						reason = extracted[1]
		else:
			mode_raw = "delete"
	else:
		text = m.text
		text = text.split(None, 1)
		stickerid = text[1]
		extracted = split_quotes(stickerid)
		duration = ""
		reason = ""
		if len(extracted) > 0:
			stickerid = extracted[0]
			if len(extracted) < 2:
				mode_raw = "delete"
			else:
				extracted1 = split_quotes(extracted[1])
				if len(extracted1) > 1:
					extracted2 = split_quotes(extracted1[1])
					if re.match(r"([0-9]{1,})([dhms])$", extracted2[0].lower()):
						duration = extracted2[0].lower()
						if len(extracted2) > 1:
							reason = extracted2[1].lower()
					else:
						reason = extracted1[1].lower()
					mode_raw = extracted1[0].lower()
				else:
					mode_raw = extracted[1].lower()
		else:
			mode_raw = text[2]
	if mode_raw == 'delete' or mode_raw == 'kick':
		duration = ""

	mode = mode_list[mode_raw]
	check = await db.find_one({'chat_id': chat_id, 'stickerid': stickerid})
	await db.update_one({'chat_id': chat_id, 'stickerid': stickerid}, {"$set": {'mode': mode, 'duration': duration, 'reason': reason}}, upsert=True)
	text = (await c.tl(chat_id, 'blsticker_added')).format(stickerid,mode_raw)
	if duration:
		text = text+(await c.tl(chat_id, 'blacklist_duration')).format(tl_time(duration))
	if reason:
		text = text+(await c.tl(chat_id, 'blacklist_reason')).format(reason)
	await m.reply_text(text,disable_web_page_preview=True)

@Mayuri.on_message(filters.command("rmblsticker", PREFIX) & admin_only)
async def rm_bl(c,m):
	db = c.db["blacklist_sticker"]
	chat_id = m.chat.id
	text = m.text
	text = text.split(None, 1)
	stickerid = ""
	if m.reply_to_message:
		sticker = m.reply_to_message.sticker
		stickerid = sticker.file_unique_id
	elif len(text) > 1:
		stickerid = text[1]
	if not stickerid:
		return await m.reply_text(await c.tl(chat_id, 'what_blacklist_to_remove'))
	check = await db.find_one({'chat_id': chat_id, 'stickerid': stickerid})
	if check:
		await db.delete_one({'chat_id': chat_id, 'stickerid': stickerid})
		await m.reply_text((await c.tl(chat_id, 'blsticker_deleted')).format(stickerid),disable_web_page_preview=True)
	else:
		await m.reply_text((await c.tl(chat_id, 'blsticker_not_found')).format(stickerid),disable_web_page_preview=True)

@Mayuri.on_message(filters.group & filters.command("blsticker", PREFIX))
@disable
async def cmd_blsticker(c,m):
	db = c.db["blacklist_sticker"]
	chat_id = m.chat.id
	list_bl = db.find({'chat_id': chat_id})
	delete = []
	mute = []
	kick = []
	ban = []
	mute_duration = []
	ban_duration = []
	if list_bl:
		async for bl in list_bl:
			if bl['mode'] == 0:
				delete.append(bl['stickerid'])
			elif bl['mode'] == 1:
				mute.append(bl['stickerid'])
				mute_duration.append(bl['duration'])
			elif bl['mode'] == 2:
				kick.append(bl['stickerid'])
			elif bl['mode'] == 3:
				ban.append(bl['stickerid'])
				ban_duration.append(bl['duration'])
		text = await c.tl(chat_id, 'blsticker_list')
		if len(delete) > 0:
			text = text+"\nDelete :\n"
			for x in delete:
				text = text+" - <code>{}</code>\n".format(x)
		if len(mute) > 0:
			text = text+"\nMute :\n"
			i = 0
			for x in mute:
				if mute_duration[i]:
					text = text+" - <code>{}</code> ({})\n".format(x,mute_duration[i])
				else:
					text = text+" - <code>{}</code>\n".format(x)
				i += 1
		if len(kick) > 0:
			text = text+"\nKick :\n"
			for x in kick:
				text = text+" - <code>{}</code>\n".format(x)
		if len(ban) > 0:
			text = text+"\nBan :\n"
			i = 0
			for x in ban:
				if ban_duration[i] == 0:
					text = text+" - <code>{}</code> ({})\n".format(x,ban_duration[i])
				else:
					text = text+" - <code>{}</code>\n".format(x)
				i += 1
		return await m.reply_text(text,disable_web_page_preview=True)
	await m.reply_text(await c.tl(chat_id, 'no_blsticker'))

@Mayuri.on_message(filters.group & filters.sticker, group=104)
async def blsticker_watcher(c,m):
	db = c.db["blacklist_sticker"]
	if m.sender_chat:
		return
	chat_id = m.chat.id
	user_id = m.from_user.id
	if await c.check_admin(chat_id,user_id) or await c.check_approved(chat_id, user_id):
		return
	mention = m.from_user.mention
	stickerid = m.sticker.file_unique_id
	reason = ""
	duration_raw = ""
	check = await db.find_one({'chat_id': chat_id, 'stickerid': stickerid})
	if not check:
		return
	if check['duration']:
		duration_raw = check['duration']
		duration = create_time(duration_raw)
	if check['reason']:
		reason = check['reason']
	mode = check['mode']
	if mode == 1:
		await m.delete()
		text = await c.tl(chat_id, 'muted')
		if duration_raw:
			await c.restrict_chat_member(chat_id, user_id, ChatPermissions(), datetime.fromtimestamp(duration))
			text += (await c.tl(chat_id, 'blacklist_for')).format(tl_time(duration_raw))
		else:
			await c.restrict_chat_member(chat_id, user_id, ChatPermissions())
		text += (await c.tl(chat_id, 'user_and_reason')).format(mention)
		if reason:
			text += "<code>{}</code>".format(reason)
		else:
			text += (await c.tl(chat_id, 'blsticker_send')).format(stickerid)
		return await m.reply_text(text,disable_web_page_preview=True)
	if mode == 2:
		await m.delete()
		text = await c.tl(chat_id, 'kicked')
		await c.ban_chat_member(chat_id,user_id)
		await c.unban_chat_member(chat_id,user_id)
		if reason:
			text += "<code>{}</code>".format(reason)
		else:
			text += (await c.tl(chat_id, 'blsticker_send')).format(stickerid)
		return await m.reply_text(text,disable_web_page_preview=True)
	if mode == 3:
		await m.delete()
		text = await c.tl(chat_id, 'banned')
		if duration_raw:
			await c.ban_chat_member(chat_id, user_id, datetime.fromtimestamp(duration))
			text += (await c.tl(chat_id, 'blacklist_for')).format(tl_time(duration_raw))
		else:
			await c.ban_chat_member(chat_id, user_id)
		text += (await c.tl(chat_id, 'user_and_reason')).format(mention)
		if reason:
			text += "<code>{}</code>".format(reason)
		else:
			text += (await c.tl(chat_id, 'bsticker_send')).format(stickerid)
		await m.reply_text(text,disable_web_page_preview=True)
