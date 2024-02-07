import asyncio

from mayuri import PREFIX
from mayuri.mayuri import Mayuri
from mayuri.util.filters import admin_only, disable, sudo_only
from pyrofork import enums, filters
from pyrofork.errors import FloodWait, RPCError

__PLUGIN__ = "admin"
__HELP__ = "admin_help"

@Mayuri.on_message(filters.command("admincache", PREFIX) & (admin_only | sudo_only))
async def admincache(c,m):
	chat_id = m.chat.id
	db = c.db["admin_list"]
	r = await m.reply_text(await c.tl(chat_id, "refreshing_admin"))
	check = await db.find_one({'chat_id': chat_id})
	admin_list = []
	try:
		all_admin = c.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
	except FloodWait as e:
		await asyncio.sleep(e.value)
	async for admin in all_admin:
		admin_list.append(admin.user.id)
	if check:
		for user_id in check["list"]:
			if user_id not in admin_list:
				await db.update_one({'chat_id': chat_id},{"$pull": {'list': user_id}})
	second_loop = False
	for user_id in admin_list:
		if check or second_loop:
			if second_loop:
				check = await db.find_one({'chat_id': chat_id})
			if user_id not in check["list"]:
				await db.update_one({'chat_id': chat_id},{"$push": {'list': user_id}})
		else:
			await db.update_one({'chat_id': chat_id},{"$push": {'list': user_id}}, upsert=True)
			second_loop = True
	await r.edit(await c.tl(chat_id, "admin_refreshed"))

@Mayuri.on_message(filters.command("adminlist", PREFIX) & filters.group)
@disable
async def cmd_adminlist(c,m):
	db = c.db["admin_list"]
	chat_id = m.chat.id
	text = await c.tl(chat_id, "admin_list_text")
	check = await db.find_one({'chat_id': chat_id})
	if not check:
		await admincache(c,m)
	for user_id in check["list"]:
		user = await c.get_chat_member(chat_id,user_id)
		if user.status == enums.ChatMemberStatus.OWNER:
			text = text+"\n • 👑 "+user.user.mention
		else:
			text = text+"\n• "+user.user.mention

	await m.reply_text(text)

@Mayuri.on_message(filters.command("approvels", PREFIX) & admin_only)
async def approvels(c,m):
	db = c.db["chat_settings"]
	chat_id = m.chat.id
	text = await c.tl(chat_id, 'admin_approved_list')
	check = await db.find_one({'chat_id': chat_id})
	if not check:
		return m.reply_text(await c.tl(chat_id, 'admin_no_approved'))
	if 'approved' not in check or len(check["approved"]) == 0:
		return m.reply_text(await c.tl(chat_id, 'admin_no_approved'))
	for user_id in check["approved"]:
		user = await c.get_users(user_id)
		mention = user.mention
		text += "\n - {}".format(mention)
	await m.reply_text(text)

@Mayuri.on_message(filters.command("approve", PREFIX) & admin_only)
async def approve(c,m):
	db = c.db["chat_settings"]
	chat_id = m.chat.id
	if m.reply_to_message:
		user_id = m.reply_to_message.from_user.id
		mention = m.reply_to_message.from_user.mention
	else:
		args = m.text.split(None,1)
		try:
			user = await c.get_users(args[1])
			user_id = user.id
			mention = user.mention
		except RPCError:
			return await m.reply_text(await c.tl(chat_id, 'need_user_id'))
	check = await db.find_one({'chat_id': chat_id})
	if check and 'approved' in check and user_id in check["approved"]:
		return m.reply_text(await c.tl(chat_id, 'user_already_approved'))
	await db.update_one({'chat_id': chat_id},{"$push": {'approved': user_id}}, upsert=True)
	text = (await c.tl(chat_id, "admin_user_added_to_approve")).format(mention)
	await m.reply_text(text)

@Mayuri.on_message(filters.command("unapprove", PREFIX) & admin_only)
async def unapprove(c,m):
	db = c.db["chat_settings"]
	chat_id = m.chat.id
	if m.reply_to_message:
		user_id = m.reply_to_message.from_user.id
		mention = m.reply_to_message.from_user.mention
	else:
		args = m.text.split(None,1)
		try:
			user = await c.get_users(args[1])
			user_id = user.id
			mention = user.mention
		except RPCError:
			return await m.reply_text(await c.tl(chat_id, 'need_user_id'))
	check = await db.find_one({'chat_id': chat_id, 'user_id': user_id})
	if check and 'approved' in check and user_id in check["approved"]:
		await db.update_one({'chat_id': chat_id},{"$pull": {'approved': user_id}})
		text = (await c.tl(chat_id, "admin_user_removed_to_approve")).format(mention)
		return await m.reply_text(text)
	m.reply_text(await c.tl(chat_id, 'user_not_approved'))

async def zombies_task(c,m):
	chat_id = m.chat.id
	msg = await m.reply_text(await c.tl(chat_id, "search_zombies"))
	await m.delete()
	count = 0
	users = []
	try:
		chat_members = c.get_chat_members(chat_id)
	except FloodWait as e:
		await asyncio.sleep(e.value)
	async for member in chat_members:
		if member.user.is_deleted and not await c.check_admin(chat_id, member.user.id):
			count = count+1
			users.append(member.user.id)

	if count == 0:
		await msg.edit(await c.tl(chat_id, "no_zombies"))
	else:
		await msg.edit((await c.tl(chat_id, "found_zombies")).format(count))
		for user in users:
			await c.ban_chat_member(chat_id,user)
		await msg.edit((await c.tl(chat_id, "zombies_cleaned")).format(count))
	await asyncio.sleep(2)
	await msg.delete()

@Mayuri.on_message(filters.command("zombies", PREFIX) & admin_only)
async def zombies(c,m):
	asyncio.create_task(zombies_task(c,m))
