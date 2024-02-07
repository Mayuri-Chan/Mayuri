from mayuri import DISABLEABLE, PREFIX
from mayuri.mayuri import Mayuri
from mayuri.util.filters import admin_only, disable
from pyrofork import filters

__PLUGIN__ = "disable"
__HELP__ = "disable_help"

@Mayuri.on_message(filters.command("disable", PREFIX) & admin_only)
async def add_to_disabled(c,m):
	chat_id = m.chat.id
	text = m.text
	text = text.split(None, 1)
	if len(text) > 1:
		cmd = text[1]
		if cmd not in DISABLEABLE:
			return await m.reply_text((await c.tl(chat_id, 'cmd_not_found')).format(cmd),disable_web_page_preview=True)
		db = c.db["chat_settings"]
		check = await db.find_one({'chat_id': chat_id})
		if check and "disabled_list" in check and cmd in check["disabled_list"]:
			return await m.reply_text((await c.tl(chat_id, 'cmd_already_disabled')).format(cmd),disable_web_page_preview=True)
		await db.update_one({'chat_id': chat_id},{"$push": {'disabled_list': cmd}}, upsert=True)
		return await m.reply_text((await c.tl(chat_id, 'cmd_disabled')).format(cmd),disable_web_page_preview=True)
	return m.reply_text(await c.tl(chat_id, 'what_cmd_to_disable'),disable_web_page_preview=True)

@Mayuri.on_message(filters.command("enable", PREFIX) & admin_only)
async def rm_from_disabled(c,m):
	chat_id = m.chat.id
	text = m.text
	text = text.split(None, 1)
	if len(text) > 1:
		cmd = text[1]
		if cmd not in DISABLEABLE:
			return await m.reply_text((await c.tl(chat_id, 'cmd_not_found')).format(cmd),disable_web_page_preview=True)
		db = c.db["chat_settings"]
		check = await db.find_one({'chat_id': chat_id})
		if not check:
			return await m.reply_text((await c.tl(chat_id, 'cmd_not_disabled')).format(cmd),disable_web_page_preview=True)
		if "disabled_list" not in check:
			return await m.reply_text((await c.tl(chat_id, 'cmd_not_disabled')).format(cmd),disable_web_page_preview=True)
		if cmd in check["disabled_list"]:
			await db.update_one({'chat_id': chat_id},{"$pull": {'disabled_list': cmd}})
			return await m.reply_text((await c.tl(chat_id, 'cmd_enabled')).format(cmd),disable_web_page_preview=True)
		return await m.reply_text((await c.tl(chat_id, 'cmd_not_disabled')).format(cmd),disable_web_page_preview=True)
	return m.reply_text(await c.tl(chat_id, 'what_cmd_to_enable'),disable_web_page_preview=True)

@Mayuri.on_message(filters.group & filters.command("disabled", PREFIX))
@disable
async def cmd_disabled(c,m):
	chat_id = m.chat.id
	db = c.db["chat_settings"]
	check = await db.find_one({'chat_id': chat_id})
	text = await c.tl(chat_id, 'disabled_list')
	if check and "disabled_list" in check:
		for cmd in check["disabled_list"]:
			text = text+" - <code>{}</code>\n".format(cmd)
		return await m.reply_text(text,disable_web_page_preview=True)
	await m.reply_text(await c.tl(chat_id, 'no_cmd_disabled'))

@Mayuri.on_message(filters.command("disableable", PREFIX) & admin_only)
async def disableable(c,m):
	chat_id = m.chat.id
	text = await c.tl(chat_id, "can_disabled")
	for cmd in DISABLEABLE:
		text = text+" - <code>{}</code>\n".format(cmd)
	await m.reply_text(text,disable_web_page_preview=True)
