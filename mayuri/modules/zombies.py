import array

from mayuri import AddHandler, Command, admin
from pyrogram import filters

@admin
async def zombies(client,message):
	chat_id = message.chat.id
	msg = await message.reply_text("Mencari akun terhapus...")
	count = 0
	users = []
	chat_members = client.iter_chat_members(chat_id)
	async for member in chat_members:
		if member.user.is_deleted:
			count = count+1
			users.append(member.user.id)

	if count == 0:
		await msg.edit("Grup bersih. tidak ada akun terhapus :)")
		return
	else:
		await msg.edit("Ditemukan {} akun terhapus.\nMembersihan...".format(count))
		for user in users:
			await client.ban_chat_member(chat_id,user)
		await msg.edit("Berhasil membersihkan {} akun terhapus".format(count))

AddHandler(zombies,filters.group & filters.command("zombies", Command))
