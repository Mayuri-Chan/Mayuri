import cv2
import os
import re
import string
import time
from mayuri import PREFIX
from mayuri.db import welcome as sql, verify as vsql
from mayuri.mayuri import Mayuri
from mayuri.utils.filters import admin_only, sudo_only
from mayuri.utils.lang import tl
from mayuri.utils.string import parse_button, build_keyboard
from pyrogram import enums, filters
from pyrogram.errors import RPCError
from pyrogram.types import InputMediaPhoto
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from random import random, choice, randint, shuffle

@Mayuri.on_message(filters.command("setwelcome", PREFIX) & admin_only)
async def set_welcome(c,m):
	chat_id = m.chat.id
	thread_id = 0
	enable = True
	clean_service = False
	is_captcha = False
	verif_text = ""
	if m.reply_to_message:
		text = m.reply_to_message.text
	else:
		text = text.split(None,1)
		text = text[1]
	check = sql.get_welcome(chat_id)
	if check:
		if not check.enable:
			enable = False
		if check.clean_service:
			clean_service = True
		if check.thread_id != 0:
			thread_id = check.thread_id
		if check.is_captcha:
			is_captcha = True
		if check.verif_text:
			verif_text = check.verif_text
	if m.chat.is_forum and (check and check.thread_id == 0):
		thread_id = m.message_thread_id
	sql.set_welcome(chat_id, text, thread_id, enable, clean_service, is_captcha, verif_text)
	r_text = await tl(chat_id, "welcome_set")
	await m.reply_text(r_text)

@Mayuri.on_message(filters.command("setwelcomethread", PREFIX) & admin_only)
async def set_thread(c,m):
	chat_id = m.chat.id
	if not m.chat.is_forum:
		return await m.reply_text(await tl(chat_id, "not_forum"))
	check = sql.get_welcome(chat_id)
	if not check:
		return await m.reply_text(await tl(chat_id, "welcome_not_set"))
	sql.set_welcome(chat_id, check.text, m.message_thread_id, check.enable, check.clean_service, False, "")
	await m.reply_text(await tl(chat_id, "thread_id_set"))

@Mayuri.on_message(filters.command("welcome", PREFIX) & admin_only)
async def welcome(c,m):
	chat_id = m.chat.id
	text = m.text
	text = text.split(None, 1)
	check = sql.get_welcome(chat_id)
	if not check:
		return await m.reply_text(await tl(chat_id, "welcome_not_set"))
	welc_settings = (await tl(chat_id, "welcome_settings")).format(check.enable, check.clean_service, check.thread_id, check.is_captcha)
	if check.verif_text:
		welc_settings += "\nVerify button text: {}".format(check.verif_text)
	if len(text) < 2:
		if not check.text:
			text = await tl(chat_id, "default-welcome")
		else:
			text = check.text
		text, button = parse_button(text)
		button = build_keyboard(button)
		if button:
			button = InlineKeyboardMarkup(button)
		else:
			button = None
		await m.reply_text(welc_settings)
		return await m.reply_text(text, reply_markup=button)
	args = text[1]
	if args in ['on', 'yes']:
		if m.chat.is_forum and check.thread_id == 0:
			thread_id = m.message_thread_id
		else:
			thread_id = check.thread_id
		sql.set_welcome(check.chat_id, check.text, thread_id, True, check.clean_service, check.is_captcha, check.verif_text)
		return await m.reply_text(await tl(chat_id, "welcome_enabled"))
	if args in ['off', 'no']:
		sql.set_welcome(check.chat_id, check.text, check.thread_id, False, check.clean_service, check.is_captcha, check.verif_text)
		return await m.reply_text(await tl(chat_id, "welcome_disabled"))
	if args == "noformat":
		await m.reply_text(welc_settings)
		return await m.reply_text(check.text, parse_mode=enums.ParseMode.DISABLED)

@Mayuri.on_message(filters.group & filters.command("welcomecaptcha", PREFIX) & admin_only)
async def set_captcha(c,m):
	chat_id = m.chat.id
	text = m.text
	text = text.split(None, 1)
	if len(text) < 2:
		return
	check = sql.get_welcome(chat_id)
	if not check:
		return await m.reply_text(await tl(chat_id, "welcome_not_set"))
	args = text[1]
	if args in ['on', 'yes']:
		if m.chat.is_forum and check.thread_id == 0:
			thread_id = m.message_thread_id
		else:
			thread_id = check.thread_id
		sql.set_welcome(check.chat_id, check.text, thread_id, check.enable, check.clean_service, True, check.verif_text)
		return await m.reply_text(await tl(chat_id, "captcha_enabled"))
	if args in ['off', 'no']:
		sql.set_welcome(check.chat_id, check.text, check.thread_id, check.enable, check.clean_service, False, check.verif_text)
		return await m.reply_text(await tl(chat_id, "captcha_disabled"))

@Mayuri.on_message(filters.group, group=10)
async def welcome_handler(c,m):
	await welcome_msg(c,m,True)

@Mayuri.on_chat_join_request()
async def join_request_handler(c,m):
	await welcome_msg(c,m,False)

async def welcome_msg(c,m,is_mute):
	chat_id = m.chat.id
	if is_mute:
		new_members = m.new_chat_members
		if not new_members:
			return
	else:
		new_members = [m.from_user]
	check = sql.get_welcome(chat_id)
	if not check or (check and not check.enable):
		return
	if check.clean_service:
		await m.delete()
	for new_member in new_members:
		if not check.text:
			text = await tl(chat_id, "default-welcome")
		else:
			text = check.text
		text, button = parse_button(text)
		button = build_keyboard(button)
		verif_text = await tl(chat_id, 'verif_text')
		if check.is_captcha:
			check2 = vsql.check_verify(chat_id,new_member.id)
			if check2:
				verify_id = check2[0].verify_id
				time_limit = check2[0].time
				msg = await c.get_messages(chat_id,check2[0].msg_id)
				await msg.delete()
			else:
				verify_id = ''.join(choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(10))
				time_limit = int(time.time()+1800)
			if is_mute:
				try:
					await c.restrict_chat_member(chat_id, new_member.id, ChatPermissions())
				except RPCError:
					pass
			if check.verif_text:
				verif_text = check.verif_text
			button.append([InlineKeyboardButton(text=verif_text, url="https://t.me/{}/start?start=verif_{}".format(c.me.username,verify_id))])
		if button:
			button = InlineKeyboardMarkup(button)
		else:
			button = None
		username = new_member.username
		if username:
			username = "@{}".format(username)
		welcome_text = (text).format(
			chatname=m.chat.title,
			first=new_member.first_name,
			last=new_member.last_name,
			fullname="{} {}".format(new_member.first_name, new_member.last_name),
			id=new_member.id,
			username=username,
			mention=new_member.mention
		)
		if not is_mute or m.chat.is_forum:
			if m.chat.is_forum:
				if check.thread_id == 0:
					return
				wc_msg = await c.send_message(chat_id=chat_id, text=welcome_text, message_thread_id=check.thread_id, reply_markup=button)
			else:
				wc_msg = await c.send_message(chat_id=chat_id, text=welcome_text, reply_markup=button)
		else:
			wc_msg = await m.reply_text(welcome_text, reply_markup=button)
		if check.is_captcha:
			vsql.add_to_verify(
				verify_id,
				chat_id,
				new_member.id,
				0,
				is_mute,
				wc_msg.id,
				time_limit
			)

def gen_math():
	first_num = str(int(random()*100))
	second_num = str(int(random()*100))
	operation = choice(['+','-','*'])
	if operation == "-" and first_num < second_num:
		operation = choice(['+','*'])
	return first_num+' '+operation+' '+second_num

def gen_math_image(math,path,bg):
	text = "{} = ?".format(math)
	image = cv2.imread("mayuri/images/bg_{}.png".format(bg))
	x_start = 120
	x_increment = [100,150]
	y = [170,180,190,200]
	fonts = [cv2.FONT_HERSHEY_SIMPLEX, cv2.FONT_HERSHEY_PLAIN, cv2.FONT_HERSHEY_DUPLEX, cv2.FONT_HERSHEY_COMPLEX, cv2.FONT_HERSHEY_TRIPLEX, cv2.FONT_HERSHEY_COMPLEX_SMALL, cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, cv2.FONT_HERSHEY_SCRIPT_COMPLEX]
	fonts2 = [cv2.FONT_HERSHEY_SIMPLEX, cv2.FONT_HERSHEY_PLAIN, cv2.FONT_HERSHEY_DUPLEX, cv2.FONT_HERSHEY_COMPLEX, cv2.FONT_HERSHEY_TRIPLEX, cv2.FONT_HERSHEY_COMPLEX_SMALL]
	colors = [(255,255,0),(255,0,0),(255,0,255),(0,255,255),(0,255,0),(0,0,255)]
	for i, line in enumerate(text.split()):
		x = x_start + i*int(choice(x_increment))
		font = choice(fonts)
		if line == "X":
			font = choice(fonts2)
		cv2.putText(img=image, text=line, org=(x, choice(y)), fontFace=font,
			fontScale=choice([3,4,5,6,7,8]), color=choice(colors), thickness=3)
	cv2.imwrite(path,image)

def gen_button(result,verify_id):
	i = 0
	numbers = []
	while(i<3):
		numbers.append(randint(1, 100))
		numbers.append(randint(1, 1000))
		numbers.append(randint(1, 10000))
		i += 1
	numbers.remove(choice(numbers))
	numbers.append(int(result))
	shuffle(numbers)
	j = 1
	buttons = []
	temp = []
	for number in numbers:
		data = "captcha_{}_{}".format(number,verify_id)
		temp.append(InlineKeyboardButton(text=number, callback_data=data))
		if j % 3 == 0:
			buttons.append(temp)
			temp = []
		if j == len(numbers):
			buttons.append(temp)
		j += 1
	buttons.append([InlineKeyboardButton(text="Regenerate", callback_data="captcha_regen_{}".format(verify_id))])
	return buttons

@Mayuri.on_message(filters.command("captcha", PREFIX) & sudo_only)
async def gen_captcha_color(c,m):
	user_id = m.from_user.id
	text = m.text.split()
	color = "dark"
	if len(text) > 1:
		if os.path.isfile("mayuri/images/bg_{}.png".format(text[1])):
			color = text[1]
	math = gen_math()
	math = math.replace("*","X")
	path = r"mayuri/images/captcha/{}.png".format(user_id)
	gen_math_image(math,path,color)
	await m.reply_photo(photo=path)
	if os.path.isfile(path):
		os.remove(path)

async def gen_captcha(m,verify_id):
	user_id = m.from_user.id
	math = gen_math()
	result = eval(math)
	math = math.replace("*","X")
	path = r"mayuri/images/captcha/{}.png".format(user_id)
	gen_math_image(math,path,"grey")
	buttons = gen_button(result,verify_id)
	return path, buttons, result

async def check_captcha_callback(_, __, query):
	if re.match(r"captcha_", query.data):
		return True

check_captcha_create = filters.create(check_captcha_callback)

@Mayuri.on_callback_query(check_captcha_create)
async def check_captcha_respond(c,q):
	m = q.message
	answer = q.data[8:13]
	if answer == "regen":
		verify_id = q.data[14:]
		path, buttons, result = await gen_captcha(m,verify_id)
		captcha_data = vsql.get_captcha(verify_id)
		if not captcha_data:
			return await c.answer_callback_query(callback_query_id=q.id, text="Requested verification key not found or expired!\nPlease rejoin the groups to request new keys.", show_alert=True)
		vsql.add_to_verify(
			verify_id,
			captcha_data.chat_id,
			captcha_data.user_id,
			result,
			captcha_data.is_mute,
			captcha_data.msg_id,
			captcha_data.time
		)
		await c.send_chat_action(m.chat.id, enums.ChatAction.UPLOAD_PHOTO)
		await m.edit_media(InputMediaPhoto(media=path, caption="Select the correct answers:"), reply_markup=InlineKeyboardMarkup(buttons))
		await c.send_chat_action(m.chat.id, enums.ChatAction.CANCEL)
		if os.path.isfile(path):
			os.remove(path)
		return
	r = re.search("(captcha_)(-{0,1}[0-9]{1,})(_)([a-zA-Z0-9]{1,})",q.data)
	answer = r.group(2)
	verify_id = r.group(4)
	captcha_data = vsql.get_captcha(verify_id)
	if captcha_data:
		correct = captcha_data.captcha
		chat_id = captcha_data.chat_id
		user_id = captcha_data.user_id
		is_mute = captcha_data.is_mute
		msg_id = captcha_data.msg_id
		time_limit = captcha_data.time
		if int(answer) == int(correct):
			if is_mute:
				try:
					curr = (await c.get_chat(chat_id)).permissions
					await c.restrict_chat_member(chat_id, user_id, curr)
				except RPCError:
					pass
			else:
				try:
					await c.approve_chat_join_request(chat_id,user_id)
				except RPCError:
					pass
			vsql.rm_from_verify(verify_id)
			if is_mute:
				caption = "Answer correct!\nYou already unmuted and can send messages in groups."
			else:
				caption = "Answer correct!\nYou already approved and can send messages in groups."
			await m.edit_media(InputMediaPhoto(media=m.photo.file_id,caption=caption))
			msg = await c.get_messages(chat_id=chat_id,message_ids=[msg_id])
			welc_data = sql.get_welcome(chat_id)
			text, button = parse_button(welc_data.text)
			button = build_keyboard(button)
			if button:
				button = button
			else:
				button = None
			user = (await c.get_users([user_id]))[0]
			if user.username:
				username = "@{}".format(user.username)
			else:
				username = None
			chat = await c.get_chat(chat_id)
			welcome_text = (text).format(
				chatname=chat.title,
				first=user.first_name,
				last=user.last_name,
				fullname="{} {}".format(user.first_name, user.last_name),
				id=user.id,
				username=username,
				mention=user.mention
			)
			return await msg[0].edit(text=welcome_text, reply_markup=button)
		await c.answer_callback_query(callback_query_id=q.id, text="Wrong answer!", show_alert=True)
		path, buttons, result = await gen_captcha(m,verify_id)
		vsql.add_to_verify(
			verify_id,
			chat_id,
			user_id,
			result,
			is_mute,
			msg_id,
			time_limit
		)
		await c.send_chat_action(m.chat.id, enums.ChatAction.UPLOAD_PHOTO)
		await m.edit_media(InputMediaPhoto(media=path, caption="Select the correct answers:"), reply_markup=InlineKeyboardMarkup(buttons))
		await c.send_chat_action(m.chat.id, enums.ChatAction.CANCEL)
		if os.path.isfile(path):
			os.remove(path)
		return
	await c.answer_callback_query(callback_query_id=q.id, text="Requested verification key not found or expired!\nPlease rejoin the groups to request new keys.", show_alert=True)

@Mayuri.on_message(group=2)
async def check_wc_exp(c,m):
	datas = vsql.get_all_captcha()
	for data in datas:
		if data.time <= time.time():
			chat_id = data.chat_id
			user_id = data.user_id
			verify_id = data.verify_id
			if data.is_mute:
				try:
					await c.ban_chat_member(chat_id,user_id)
					await c.unban_chat_member(chat_id,user_id)
				except RPCError:
					pass
			else:
				try:
					await c.decline_chat_join_request(chat_id,user_id)
				except RPCError:
					pass
			vsql.rm_from_verify(verify_id)
			msg = await c.get_messages(chat_id=data.chat_id,message_ids=[data.msg_id])
			await msg[0].delete()
