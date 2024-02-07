from mayuri import PREFIX
from mayuri.mayuri import Mayuri
from mayuri.util.filters import admin_only
from pyrofork import filters

__PLUGIN__ = "rules"
__HELP__ = "rules_help"

@Mayuri.on_message(filters.command("setrules", PREFIX) & admin_only)
async def set_rules(c,m):
	db = c.db["chat_settings"]
	chat_id = m.chat.id
	if m.reply_to_message:
		text = m.reply_to_message.text
	else:
		args = m.text.split(None,1)
		text = args[1]
	await db.update_one({'chat_id': chat_id},{"$set": {'rules': text}}, upsert=True)
	text = (await c.tl(chat_id, "rules_set"))
	await m.reply_text(text)

@Mayuri.on_message(filters.command("rules", PREFIX))
async def rules(c,m):
	db = c.db["chat_settings"]
	chat_id = m.chat.id
	check = await db.find_one({'chat_id': chat_id})
	if check and 'rules' in check:
		text = await c.tl(chat_id, "rules_for_this_group")
		text += check['rules']
		return await m.reply_text(text)
	await m.reply_text(await c.tl(chat_id, 'no_rules'))
