import array
from mayuri import bot

async def adminlist(client,chat_id):
	all = client.iter_chat_members(chat_id, filter="administrators")
	admin = []
	async for a in all:
		admin.append(a.user.id)
	return admin
