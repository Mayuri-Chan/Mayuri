import asyncio
import os
import re

from datetime import datetime
from mayuri import PREFIX, USE_OCR
from mayuri.db import blacklist as sql
from mayuri.mayuri import Mayuri
from mayuri.plugins.admin import check_admin
from mayuri.utils.filters import admin_only, disable
from mayuri.utils.lang import tl
from mayuri.utils.misc import check_approve
from mayuri.utils.string import split_quotes
from mayuri.utils.time import create_time, tl_time
from pyrogram import filters
from pyrogram.types import ChatPermissions
from unidecode import unidecode

__PLUGIN__ = "blacklist"
__HELP__ = "blacklist_help"

@Mayuri.on_message(filters.command("addbl", PREFIX) & admin_only)
async def addbl(c,m):
	chat_id = m.chat.id
	mode_list = {'delete': 0,'mute': 1, 'kick': 2,'ban': 3}
	text = m.text
	text = text.split(None, 1)
	trigger = text[1].lower()
	extracted = split_quotes(trigger)
	duration = ""
	reason = ""
	if len(extracted) > 0:
		trigger = extracted[0]
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

	sql.add_to_blacklist(chat_id,trigger,mode,reason,duration)
	text = (await tl(chat_id, 'blacklist_added')).format(trigger,mode_raw)
	if duration:
		text = text+(await tl(chat_id, 'blacklist_duration')).format(duration)
	if reason:
		text = text+(await tl(chat_id, 'blacklist_reason')).format(reason)
	await m.reply_text(text,disable_web_page_preview=True)

@Mayuri.on_message(filters.command("rmbl", PREFIX) & admin_only)
async def rm_bl(c,m):
	chat_id = m.chat.id
	text = m.text
	text = text.split(None, 1)
	if len(text) > 1:
		trigger = text[1]
		extracted = split_quotes(trigger)
		if len(extracted) > 0:
			trigger = extracted[0].lower()

		if sql.rm_from_blacklist(chat_id,trigger):
			await m.reply_text((await tl(chat_id, 'blacklist_deleted')).format(trigger),disable_web_page_preview=True)
		else:
			await m.reply_text((await tl(chat_id, 'cannot_remove_blacklist')).format(trigger),disable_web_page_preview=True)
	else:
		await m.reply_text(await tl(chat_id, 'what_blacklist_to_remove'))

@Mayuri.on_message(filters.group & disable("blacklist"))
async def blacklist_list(c,m):
	chat_id = m.chat.id
	list_trigger = sql.blacklist_list(chat_id)
	delete = []
	mute = []
	kick = []
	ban = []
	mute_duration = []
	ban_duration = []
	if list_trigger:
		for trigger in list_trigger:
			if trigger.mode == 0:
				delete.append(trigger.trigger)
			elif trigger.mode == 1:
				mute.append(trigger.trigger)
				mute_duration.append(trigger.duration)
			elif trigger.mode == 2:
				kick.append(trigger.trigger)
			elif trigger.mode == 3:
				ban.append(trigger.trigger)
				ban_duration.append(trigger.duration)
		text = await tl(chat_id, 'blacklist_list')
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
	await m.reply_text(await tl(chat_id, 'no_blacklist'))

async def blacklist_task(c,m):
	chat_id = m.chat.id
	user_id = m.from_user.id
	mention = m.from_user.mention
	text = ""
	text2 = ""
	reason = ""
	duration_raw = ""
	mt = ['image/jpeg', 'image/png']
	if m.sticker:
		text = m.sticker.emoji
	elif m.caption:
		text = unidecode(m.caption).lower()
	elif m.text:
		text = unidecode(m.text).lower()
	if m.photo or m.sticker or (m.document and m.document.mime_type in mt):
		if m.photo:
			target = "images/bl/{}.jpg".format(m.photo.file_id)
		elif m.sticker:
			if m.sticker.is_animated or m.sticker.is_video:
				return
			target = "images/bl/{}.webp".format(m.sticker.file_id)
		elif m.document:
			if m.document.mime_type == "image/jpeg":
				target = "images/bl/{}.jpg".format(m.document.file_id)
			else:
				target = "images/bl/{}.png".format(m.document.file_id)
		if USE_OCR:
			import cv2
			import pytesseract
			await m.download(target)
			if not os.path.exists(target):
				target = "mayuri/"+target
			im = cv2.imread(target)
			im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
			try:
				text2 = pytesseract.image_to_string(im, config='--oem 3 --psm 12').lower()
			except RuntimeError:
				text2 = ""
			os.remove(target)
	if not text and not text2:
		return
	data_list = []
	mode_list = []
	check = sql.blacklist_list(chat_id)
	if not check:
		return

	for trigger in check:
		ch = re.search(trigger.trigger.replace('"',''),text)
		ch2 = re.search(trigger.trigger.replace('"',''),text2)
		if ch or ch2:
			data = {
				'trigger': trigger.trigger,
				'mode': trigger.mode,
				'reason': trigger.reason,
				'duration': trigger.duration
			}
			if trigger.mode == 0:
				data_list.append(data)
				if trigger.mode not in mode_list:
					mode_list.append(trigger.mode)
			elif trigger.mode == 1:
				data_list.append(data)
				if trigger.mode not in mode_list:
					mode_list.append(trigger.mode)
			elif trigger.mode == 2:
				data_list.append(data)
				if trigger.mode not in mode_list:
					mode_list.append(trigger.mode)
			elif trigger.mode == 3:
				data_list.append(data)
				if trigger.mode not in mode_list:
					mode_list.append(trigger.mode)

	mode_list.sort()
	curr_duration = 0
	curr_unit = ""
	if len(mode_list) > 0:
		mode = mode_list[len(mode_list)-1]
		for data in data_list:
			if data["mode"] == mode:
				curr_duration_raw = data["duration"]
				if not curr_duration_raw:
					duration_raw = data["duration"]
					trigger = data["trigger"]
					reason = data["reason"]
					break
				else:
					duration_unit = curr_duration_raw[len(curr_duration_raw)-1]
					duration_time = int(curr_duration_raw[0:len(curr_duration_raw)-1])
					if not curr_duration:
						curr_duration = duration_time
						curr_unit = duration_unit
						duration_raw = curr_duration_raw
						trigger = data["trigger"]
						reason = data["reason"]
					elif curr_unit ==  duration_unit:
						if curr_duration < duration_time:
							curr_duration = duration_time
							duration_raw = curr_duration_raw
							trigger = data["trigger"]
							reason = data["reason"]
					elif (
						duration_unit == 'm' and curr_unit == 's' or
						duration_unit == 'h' and curr_unit in ['s','m'] or
						duration_unit == 'd' and curr_unit in ['s', 'm', 'h']
					):
						curr_duration = duration_time
						curr_unit = duration_unit
						duration_raw = curr_duration_raw
						trigger = data["trigger"]
						reason = data["reason"]
	else:
		return
	if duration_raw:
		duration = create_time(duration_raw)
	if mode == 0:
		await m.delete()
	if mode == 1:
		await m.delete()
		text = await tl(chat_id, 'muted')
		if duration_raw:
			await c.restrict_chat_member(chat_id, user_id, ChatPermissions(), datetime.fromtimestamp(duration))
			text += (await tl(chat_id, 'blacklist_for')).format(tl_time(duration_raw))
		else:
			await c.restrict_chat_member(chat_id, user_id, ChatPermissions())
		text += (await tl(chat_id, 'user_and_reason')).format(mention)
		if reason:
			text += "<code>{}</code>".format(reason)
		else:
			text += (await tl(chat_id, 'blacklist_said')).format(trigger)
		return await m.reply_text(text,disable_web_page_preview=True)
	if mode == 2:
		await m.delete()
		text = await tl(chat_id, 'kicked')
		await c.ban_chat_member(chat_id,user_id)
		await c.unban_chat_member(chat_id,user_id)
		if reason:
			text += "<code>{}</code>".format(reason)
		else:
			text += (await tl(chat_id, 'blacklist_said')).format(trigger)
		return await m.reply_text(text,disable_web_page_preview=True)
	if mode == 3:
		await m.delete()
		text = await tl(chat_id, 'banned')
		if duration_raw:
			await c.ban_chat_member(chat_id, user_id, datetime.fromtimestamp(duration))
			text += (await tl(chat_id, 'blacklist_for')).format(tl_time(duration_raw))
		else:
			await c.ban_chat_member(chat_id, user_id)
		text += (await tl(chat_id, 'user_and_reason')).format(mention)
		if reason:
			text += "<code>{}</code>".format(reason)
		else:
			text += (await tl(chat_id, 'blacklist_said')).format(trigger)
		await m.reply_text(text,disable_web_page_preview=True)

@Mayuri.on_message(filters.group, group=102)
async def bl(c,m):
	if m.sender_chat:
		return
	chat_id = m.chat.id
	user_id = m.from_user.id
	if await check_admin(chat_id,user_id) or await check_approve(chat_id, user_id):
		return
	asyncio.create_task(blacklist_task(c,m))
