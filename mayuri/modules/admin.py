import array
from mayuri import bot, Command
from mayuri.modules.disableable import DisableAbleHandler, CheckDisable
from pyrogram import filters

async def get_adminlist(client,message):
	chat_id = message.chat.id
	check = CheckDisable(chat_id, message.text)
	if check:
		return

	bot_id = (await client.get_me()).id
	all = client.iter_chat_members(chat_id, filter="administrators")
	text = "**Daftar Admin di Grup Ini**\n"
	async for admin in all:
		if admin.status == "creator":
			text = text+"Creator : \n • "+admin.user.mention


	all = client.iter_chat_members(chat_id, filter="administrators")
	text = text+"\n\nAdmin : "
	async for a in all:
		if (a.status == "administrator" and not a.user.is_bot) or (a.user.is_bot and a.user.id == bot_id):
			text = text+"\n • "+a.user.mention

	await message.reply_text(text)

DisableAbleHandler(get_adminlist,filters.group & filters.command("adminlist", Command),"adminlist")
