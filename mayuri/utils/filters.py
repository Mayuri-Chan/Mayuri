from mayuri import OWNER
from mayuri.db import admin as admin_db, sudo as sudo_db
from pyrogram import filters

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

owner_only = filters.create(owner_check)
sudo_only = filters.create(sudo_check)
admin_only = filters.create(admin_check)
