from mayuri import DISABLEABLE, PREFIX
from mayuri.db import disable as sql
from mayuri.mayuri import Mayuri
from mayuri.utils.filters import admin_only, disable
from mayuri.utils.lang import tl
from pyrogram import filters

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
			return await m.reply_text((await tl(chat_id, 'cmd_not_found')).format(cmd),disable_web_page_preview=True)
		sql.add_to_disabled(chat_id, cmd)
		return await m.reply_text((await tl(chat_id, 'cmd_disabled')).format(cmd),disable_web_page_preview=True)
	return m.reply_text(await tl(chat_id, 'what_cmd_to_disable'),disable_web_page_preview=True)

@Mayuri.on_message(filters.command("enable", PREFIX) & admin_only)
async def rm_from_disabled(c,m):
	chat_id = m.chat.id
	text = m.text
	text = text.split(None, 1)
	if len(text) > 1:
		cmd = text[1]
		if cmd not in DISABLEABLE:
			return await m.reply_text((await tl(chat_id, 'cmd_not_found')).format(cmd),disable_web_page_preview=True)
		sql.rm_from_disabled(chat_id, cmd)
		return await m.reply_text((await tl(chat_id, 'cmd_enabled')).format(cmd),disable_web_page_preview=True)
	return m.reply_text(await tl(chat_id, 'what_cmd_to_enable'),disable_web_page_preview=True)

@Mayuri.on_message(filters.group & disable("disabled"))
async def disabled(c,m):
	chat_id = m.chat.id
	cmd_list = sql.disabled_list(chat_id)
	text = await tl(chat_id, 'disabled_list')
	if cmd_list:
		for cmd in cmd_list:
			text = text+" - <code>{}</code>\n".format(cmd.cmd)
		await m.reply_text(text,disable_web_page_preview=True)
	else:
		await m.reply_text(await tl(chat_id, 'no_cmd_disabled'))

@Mayuri.on_message(filters.command("disableable", PREFIX) & admin_only)
async def disableable(c,m):
	chat_id = m.chat.id
	text = await tl(chat_id, "can_disabled")
	for cmd in DISABLEABLE:
		text = text+" - <code>{}</code>\n".format(cmd)
	await m.reply_text(text,disable_web_page_preview=True)
