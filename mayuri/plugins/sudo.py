from mayuri import PREFIX
from mayuri.mayuri import Mayuri
from mayuri.util.filters import owner_only
from pyrofork import filters
from pyrofork.errors import RPCError

@Mayuri.on_message(filters.command("addsudo", PREFIX) & owner_only)
async def add_sudo(c,m):
	db = c.db["bot_settings"]
	chat_id = m.chat.id
	if m.reply_to_message:
		user_id = m.reply_to_message.from_user.id
		mention = m.reply_to_message.from_user.mention
	else:
		args = m.text.split(None,2)
		try:
			user = await c.get_users(args[1])
			user_id = user.id
			mention = user.mention
		except RPCError:
			await m.reply_text(await c.tl(chat_id, "not_user"))
			return
	check = await db.find_one({'name': 'sudo_list'})
	if check and user_id in check["list"]:
		return await m.reply_text((await c.tl(chat_id, "user_is_sudo")).format(mention))
	await db.update_one({'name': 'sudo_list'},{"$push": {'list': user_id}}, upsert=True)
	text = (await c.tl(chat_id, "added_to_sudo")).format(mention)
	await m.reply_text(text)

@Mayuri.on_message(filters.command("rmsudo", PREFIX) & owner_only)
async def rm_sudo(c,m):
	db = c.db["bot_settings"]
	chat_id = m.chat.id
	if m.reply_to_message:
		user_id = m.reply_to_message.from_user.id
		mention = m.reply_to_message.from_user.mention
	else:
		args = m.text.split(None,2)
		try:
			user = await c.get_users(args[1])
			user_id = user.id
			mention = user.mention
		except RPCError:
			await m.reply_text(await c.tl(chat_id, "not_user"))
			return
	check = await db.find_one({'name': 'sudo_list'})
	if not check:
		return await m.reply_text((await c.tl(chat_id, "user_is_not_sudo")).format(mention))
	if user_id not in check["list"]:
		return await m.reply_text((await c.tl(chat_id, "user_is_not_sudo")).format(mention))
	await db.update_one({'name': 'sudo_list'},{"$pull": {'list': user_id}})
	text = (await c.tl(chat_id, "removed_from_sudo")).format(mention)
	await m.reply_text(text)

@Mayuri.on_message(filters.command("sudols", PREFIX) & owner_only)
async def sudols(c,m):
	db = c.db["bot_settings"]
	chat_id = m.chat.id
	text = await c.tl(chat_id, "sudo_ls")
	check = await db.find_one({'name': 'sudo_list'})
	if not check:
		return await m.reply_text((await c.tl(chat_id, "no_sudo")))
	for user_id in check["list"]:
		user = await c.get_users(user_id)
		mention = user.mention
		text += "\n - {}".format(mention)
	await m.reply_text(text)
