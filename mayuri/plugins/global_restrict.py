from mayuri.mayuri import Mayuri
from pyrogram import filters

@Mayuri.on_message(filters.group, group=1)
async def chat_watcher(c,m):
	db = c.db["chat_list"]
	chat_id = m.chat.id
	await db.update_one({'chat_id': chat_id},{"$set": {'chat_username': m.chat.username, 'chat_name': m.chat.title}}, upsert=True)
