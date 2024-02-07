from mayuri import PREFIX
from mayuri.mayuri import Mayuri
from mayuri.util.filters import admin_only, disable
from mayuri.util.string import split_quotes, parse_button, build_keyboard
from pyrofork import filters
from pyrofork.types import InlineKeyboardMarkup

__PLUGIN__ = "filters"
__HELP__ = "filters_help"

@Mayuri.on_message(filters.command("filter", PREFIX) & admin_only)
async def addfilter(c,m):
	db = c.db["filters"]
	chat_id = m.chat.id
	reply = m.reply_to_message
	text = m.text
	text = text.split(None, 1)
	filt_type = 0
	value = ""
	document = ""
	document_type = 0
	name = text[1]
	extracted = split_quotes(name)
	if reply:
		if len(extracted) < 1:
			return await m.reply_text(await c.tl(chat_id, 'give_filter_name'))
		name = (extracted[0]).lower()
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
			text, _ = parse_button(value)
			text = text.strip()
			if not text:
				return await m.reply_text()
	else:
		if len(extracted) <= 1:
			return await m.reply_text(await c.tl(chat_id, 'give_filter_text'))
		filt_type = 1
		name = extracted[0]
		value = extracted[1]
		text, _ = parse_button(value)
		text = text.strip()
		if not text:
			return await m.reply_text(await c.tl(chat_id, 'give_filter_text'))
	await db.update_one({'chat_id': chat_id, 'name': name},{"$set": {'value': value, 'type': filt_type, 'media': document, 'media_type': document_type}}, upsert=True)
	await m.reply_text((await c.tl(chat_id, 'filter_added')).format(name,m.chat.title),disable_web_page_preview=True)

@Mayuri.on_message(filters.command("stop", PREFIX) & admin_only)
async def rm_filter(c,m):
	db = c.db["filters"]
	chat_id = m.chat.id
	text = m.text
	text = text.split(None, 1)
	if len(text) > 1:
		name = text[1]
		extracted = split_quotes(name)
		if len(extracted) > 0:
			name = extracted[0].lower()
		check = await db.find_one({'chat_id': chat_id, 'name': name})
		if check:
			await db.delete_one({'chat_id': chat_id, 'name': name})
			await m.reply_text((await c.tl(chat_id, 'filter_removed')).format(name,m.chat.title),disable_web_page_preview=True)
		else:
			await m.reply_text((await c.tl(chat_id, 'filter_not_found')).format(name),disable_web_page_preview=True)
	else:
		await m.reply_text(await c.tl(chat_id, 'what_filter_to_remove'))

@Mayuri.on_message(filters.group & filters.command("filters", PREFIX))
@disable
async def cmd_filters(c,m):
	db = c.db["filters"]
	chat_id = m.chat.id
	list_name = db.find({'chat_id': chat_id})
	text = await c.tl(chat_id, 'filter_list')
	if list_name:
		async for filt in list_name:
			text = text+" - <code>{}</code>\n".format(filt['name'])
		await m.reply_text(text,disable_web_page_preview=True)
	else:
		await m.reply_text((await c.tl(chat_id, 'no_filter_found')).format(m.chat.title))

@Mayuri.on_message(filters.group, group=103)
async def filter_watcher(c,m):
	db = c.db["filters"]
	chat_id = m.chat.id
	if m.caption:
		text = m.caption
	else:
		text = m.text
	if not text:
		return
	if m.command and (m.command[0]).lower() in ['filter', 'stop']:
		return
	text = text.lower()
	text = text.split()
	check = db.find({'chat_id': chat_id})
	if m.sender_chat:
		chat = m.sender_chat
		if chat.username:
			mention = f"[{chat.title}](https://t.me/{chat.username})"
		else:
			mention = None
		first_name = chat.title
		last_name = ""
		fullname = chat.title
		user_id = chat.id
		user_name = chat.username
	else:
		mention = m.from_user.mention
		first_name = m.from_user.first_name
		last_name = m.from_user.last_name
		fullname = "{} {}".format(first_name,last_name)
		user_id = m.from_user.id
		user_name = m.from_user.username
	value = ""
	if not check:
		return
	async for filt in check:
		if filt['name'] in text:
			value = filt['value']
			if value:
				text, button = parse_button(value)
				button = build_keyboard(button)
				if button:
					button = InlineKeyboardMarkup(button)
				else:
					button = None
			else:
				text = ""
				button = None

			text.format(
				first_name=first_name,
				last_name=last_name,
				fullname=fullname,
				user_id=user_id,
				user_name=user_name,
				mention=mention
			)
			if filt['type'] == 1:
				await m.reply_text(text,
					reply_markup=button
				)
			elif filt['type'] == 3:
				await m.reply_sticker(filt['media'])
			elif filt['type'] == 4:
				if filt['media_type'] == 1:
					await m.reply_audio(audio=filt['media'],caption=text,reply_markup=button)
				elif filt['media_type'] == 2:
					await m.reply_document(document=filt['media'],caption=text,reply_markup=button)
				elif filt['media_type'] == 3:
					await m.reply_photo(photo=filt['media'],caption=text,reply_markup=button)
				elif filt['media_type'] == 4:
					await m.reply_video(video=filt['media'],caption=text,reply_markup=button)
			break
