from mayuri import DISABLEABLE, OWNER, PREFIX
from mayuri.db import admin as admin_db, disable as disable_db, sudo as sudo_db
from pyrogram import enums, filters

async def owner_check(_, __, m):
	user_id = m.from_user.id
	if user_id == OWNER:
		return True
	return False

async def sudo_check(_, __, m):
	user_id = m.from_user.id
	check = sudo_db.check_sudo(user_id)
	owner = await owner_check(_, __, m)
	if check or owner:
		return True
	return False

async def admin_check(_, __, m):
	chat_id = m.chat.id
	user_id = m.from_user.id
	if admin_db.check_admin(chat_id,user_id):
		return True
	return False

def disable(cmd):
	if cmd not in DISABLEABLE:
		DISABLEABLE.append(cmd)

	async def decorator(_, c, m):
		if not m.text:
			return False
		text = (m.text.split(None, 1))[0]
		text = text.replace("@{}".format(c.me.username), '')
		is_disabled = False
		if text.startswith(tuple(PREFIX)) and text[1:] == cmd:
			if m.chat.type == enums.ChatType.PRIVATE:
				return True
			if await admin_check(_, c, m):
				return True
			is_disabled = disable_db.check_disabled(m.chat.id, cmd)
			if not is_disabled:
				return True
		return False
	return filters.create(decorator)


owner_only = filters.create(owner_check)
sudo_only = filters.create(sudo_check)
admin_only = filters.create(admin_check)
