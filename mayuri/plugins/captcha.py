import os
import random
import re
from mayuri import PREFIX
from mayuri.mayuri import Mayuri
from mayuri.util.string import parse_button, build_keyboard
from PIL import Image
from pyrofork import filters
from pyrofork.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, ReplyKeyboardRemove

__PLUGIN__ = "captcha"
__HELP__ = "captcha_help"

async def getCAPTCHAJPG(user_id):
	EmojiBank = ['🐻', '🐔', '☁️', '🔮', '🌀', '🌚', '💎', '🐶', '🍩', '🌏', '🐸', '🌕', '🍏', '🐵', '🌙',
				'🐧', '🍎', '😀', '🐍', '❄️', '🐚', '🐢', '🌝', '🍺', '🍔', '🍒', '🍫', '🍡', '💣', '🍟',
				'🇮🇷', '🍑', '🍷', '🍧', '🍕', '🍵', '🐋', '🐱', '💄', '👠', '💰', '💸', '🎹', '📦', '📍',
				'🐊', '🦕', '🐬', '💋', '🦎', '🦈', '🦷', '🦖', '🐠', '🐟','💀', '🎃', '👮', '⛑️', '🪢', '🧶',
				'🧵', '🪡', '🧥', '🥼', '🥻', '🎩', '👑', '🎒', '🙊', '🐗', '🦋', '🦐', '🐀', '🎻', '🦔', '🦦', 
				'🦫', '🦡', '🦨', '🐇']
	EmojiIndex= [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 
				31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 
				57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80]
	captchaAnswer = []
	positions = [[520,260],[160,200],[420,190],[240,300], [400,300], [300,200]]
	rotations = [120, 80, 40, 90, 50, 50]
	i = 0
	base_img = Image.open(r"mayuri/images/base.png").convert('RGB')
	while True:
		EmojiRandomSelect = random.choice(EmojiIndex)
		if EmojiRandomSelect in captchaAnswer:
			continue
		captchaAnswer.append(EmojiBank[EmojiRandomSelect])
		position = ((base_img.width - positions[i][0]) , (base_img.height - positions[i][1]))
		base_img.paste(
			Image.open(rf"mayuri/images/emojis/{EmojiBank[EmojiRandomSelect]}.png").resize((60 , 60)).rotate(rotations[i]),
			position,Image.open(rf"mayuri/images/emojis/{EmojiBank[EmojiRandomSelect]}.png").resize((60 , 60)).rotate(rotations[i])
		)
		if i == 5:
			break
		i = i+1

	file_name = f"mayuri/images/captcha/captcha_{user_id}.png"
	base_img.save(file_name)
	return captchaAnswer, file_name

async def gen_button(verify_id, answer):
	_emojis = ['🐻', '🐔', '☁️', '🔮', '🌀', '🌚', '💎', '🐶', '🍩', '🌏', '🐸', '🌕', '🍏', '🐵', '🌙',
					'🐧', '🍎', '😀', '🐍', '❄️', '🐚', '🐢', '🌝', '🍺', '🍔', '🍒', '🍫', '🍡', '💣', '🍟',
					'🇮🇷', '🍑', '🍷', '🍧', '🍕', '🍵', '🐋', '🐱', '💄', '👠', '💰', '💸', '🎹', '📦', '📍',
					'🐊', '🦕', '🐬', '💋', '🦎', '🦈', '🦷', '🦖', '🐠', '🐟','💀', '🎃', '👮', '⛑️', '🪢', '🧶',
					'🧵', '🪡', '🧥', '🥼', '🥻', '🎩', '👑', '🎒', '🙊', '🐗', '🦋', '🦐', '🐀', '🎻', '🦔', '🦦', 
					'🦫', '🦡', '🦨', '🐇']
	all_emoji = []
	for emoji in answer:
		all_emoji.append(emoji)
	while True:
		emo = random.choice(_emojis)
		if emo not in all_emoji:
			all_emoji.append(emo)
		if len(all_emoji) == 16:
			break

	random.shuffle(all_emoji)
	i = 1
	''' Python List Duplication features
	buttons = []
	for emo in all_emoji:
		if i == 1:
			button = []
			button.append(InlineKeyboardButton(emo, callback_data=f"_captcha_{verify_id}_{emo}"))
		elif i in [5,9,13]:
			button.clear()
			button.append(InlineKeyboardButton(emo, callback_data=f"_captcha_{verify_id}_{emo}"))
		elif i%4 == 0:
			button.append(InlineKeyboardButton(emo, callback_data=f"_captcha_{verify_id}_{emo}"))
			buttons.append(button)
		else:
			button.append(InlineKeyboardButton(emo, callback_data=f"_captcha_{verify_id}_{emo}"))
		i = i+1
	'''

	buttons = [[],[],[],[]]
	j = 0
	for emo in all_emoji:
		buttons[j].append(InlineKeyboardButton(emo, callback_data=f"_captcha_{verify_id}_{emo}"))
		if i%4 == 0:
			j = j+1
		i = i+1
	return buttons

async def gen_captcha(verify_id,user_id):
	answer, file_name = await getCAPTCHAJPG(user_id)
	buttons = await gen_button(verify_id, answer)
	return answer, file_name, buttons

async def make_markup(markup, __emoji, indicator):
	'''
	use weird List inside for loop features
	In :
	def test(number):
	    _number = number[0]
	    for i in range(5):
	    	_number.append(i)

	a = [[20],[21]]
	test(a)
	print(a)

	Out:
	[[20, 0, 1, 2, 3, 4], [21]]
	'''
	for i in markup:
		for k in i:
			if k.text == __emoji:
				k.text = indicator
				k.callback_data = "_captcha_picked"

async def reload_captcha(c, m, db, chat_id, verify_id, user_id, msg_id):
	answer, file_name, buttons = await gen_captcha(verify_id,user_id)
	buttons.append([InlineKeyboardButton("🔄", callback_data=f"_captcha_regen_{verify_id}")])
	await m.edit_media(media=InputMediaPhoto(media=file_name, caption=(await c.tl(user_id, 'select_all_emojis'))), reply_markup=InlineKeyboardMarkup(buttons))
	await db.update_one({'verify_id': verify_id},{"$set": {'chat_id': chat_id,'user_id': user_id, 'answer': answer, 'right': 0, 'wrong': 0, 'msg_id': msg_id}}, upsert=True)
	return os.remove(file_name)

async def check_captcha_callback(_, __, query):
	if re.match(r"_captcha_", query.data):
		return True

check_captcha_create = filters.create(check_captcha_callback)

@Mayuri.on_callback_query(check_captcha_create)
async def check_respond(c, q):
	db = c.db['captcha_list']
	m = q.message
	user_id = q.from_user.id
	regen = re.match("(_captcha_regen_)",q.data)
	if regen:
		verify_id = q.data[15:]
		check = await db.find_one({'verify_id': verify_id})
		if check:
			chat_id = check['chat_id']
			msg_id = check['msg_id']
			await m.edit_text(await c.tl(m.chat.id, 'regenerate_captcha'))
			return await c.loop.create_task(reload_captcha(c, m, db, chat_id, verify_id, user_id, msg_id))
		return await m.edit_caption(await c.tl(user_id, 'verify_id_not_found'))

	if re.match("(_captcha_picked)",q.data):
		return await q.answer("You already pick that one!")
	r = re.search("(_captcha_)([a-zA-Z0-9]{1,})(_)(.*)",q.data)
	verify_id = r.group(2)
	answer = r.group(4)
	check = await db.find_one({'verify_id': verify_id})
	if check and check['user_id'] == user_id:
		right = check['right']
		wrong = check['wrong']
		msg_id = check['msg_id']
		if answer in check['answer']:
			right = right+1
			reply_markup = m.reply_markup
			await make_markup(reply_markup.inline_keyboard, answer, "✅")
			await m.edit_reply_markup(reply_markup=reply_markup)
			await db.update_one({'verify_id': verify_id},{"$set": {'right': right}})
		else:
			wrong = wrong+1
			reply_markup = m.reply_markup
			await make_markup(reply_markup.inline_keyboard, answer, "❌")
			await m.edit_reply_markup(reply_markup=reply_markup)
			await db.update_one({'verify_id': verify_id},{"$set": {'wrong': wrong}})
		if wrong >= 3:
			return await c.loop.create_task(reload_captcha(m, db, check['chat_id'], verify_id, user_id, msg_id))
		if right >= 6:
			await m.edit_caption("Well done.")
			try:
				if not check['is_request']:
					permissions = (await c.get_chat(check["chat_id"])).permissions
					await c.restrict_chat_member(check["chat_id"],user_id, permissions)
				else:
					await c.approve_chat_join_request(check["chat_id"],user_id)
			except Exception as e:
				c.log.error(f"{e}")
			else:
				await db.delete_one({'verify_id': verify_id})

			try:
				msg = await c.get_messages(check['chat_id'], check['msg_id'])
				if msg:
					welcome_db = c.db['welcome_settings']
					welcome_set = await welcome_db.find_one({'chat_id': check['chat_id']})
					if not welcome_set['text']:
						text = await c.tl(check['chat_id'], "default-welcome")
					else:
						text = welcome_set['text']
					text, buttons = parse_button(text)
					buttons = build_keyboard(buttons)
					if buttons:
						buttons = InlineKeyboardButton(buttons)
					else:
						buttons = None
					username = q.from_user.username
					if username:
						username = "@{}".format(username)
					chat = await c.get_chat(check['chat_id'])
					welcome_text = (text).format(
						chatname=chat.title,
						first=q.from_user.first_name,
						last=q.from_user.last_name,
						fullname="{} {}".format(q.from_user.first_name, q.from_user.last_name),
						id=q.from_user.id,
						username=username,
						mention=q.from_user.mention
					)
					if welcome_set['media']:
						return await msg.edit_caption(caption=welcome_text, reply_markup=buttons)
					await msg.edit_text(text=welcome_text, reply_markup=buttons)
			except Exception as e:
				c.log.error(f"{e}")

@Mayuri.on_message(filters.private, group=11)
async def tunstile_watcher(c,m):
	db = c.db['captcha_list']
	user_id = m.chat.id
	if not m.web_app_data:
		return
	data = json.loads(m.web_app_data.data)
	if not data['success']:
		return await m.reply_text((await c.tl(user_id, 'verification_failed')))
	verify_id = data['verify_id']
	check = await db.find_one({'verify_id': verify_id})
	if check and check['user_id'] == user_id:
		msg_id = check['msg_id']
		await m.reply_text("Well done.", reply_markup=ReplyKeyboardRemove())
		try:
			if not check['is_request']:
				permissions = (await c.get_chat(check["chat_id"])).permissions
				await c.restrict_chat_member(check["chat_id"],user_id, permissions)
			else:
				await c.approve_chat_join_request(check["chat_id"],user_id)
		except Exception as e:
			c.log.exception(e)
		else:
			await db.delete_one({'verify_id': verify_id})

		try:
			msg = await c.get_messages(check['chat_id'], check['msg_id'])
			if msg:
				welcome_db = c.db['welcome_settings']
				welcome_set = await welcome_db.find_one({'chat_id': check['chat_id']})
				if not welcome_set['text']:
					text = await c.tl(check['chat_id'], "default-welcome")
				else:
					text = welcome_set['text']
				text, buttons = parse_button(text)
				buttons = build_keyboard(buttons)
				if buttons:
					buttons = InlineKeyboardButton(buttons)
				else:
					buttons = None
				user = await c.get_users(user_id)
				username = user.username
				if username:
					username = "@{}".format(username)
				chat = await c.get_chat(check['chat_id'])
				welcome_text = (text).format(
					chatname=chat.title,
					first=user.first_name,
					last=user.last_name,
					fullname="{} {}".format(user.first_name, user.last_name),
					id=user.id,
					username=username,
					mention=user.mention
				)
				if welcome_set['media']:
					return await msg.edit_caption(caption=welcome_text, reply_markup=buttons)
				await msg.edit_text(text=welcome_text, reply_markup=buttons)
		except Exception as e:
			c.log.exception(e)
