import asyncio
import time

from datetime import datetime
from mayuri import API_ID, API_HASH, BOT_SESSION, BOT_TOKEN, WORKERS, init_help, scheduler
from mayuri.db import admin as asql, global_restrict as grsql
from mayuri.plugins import list_all_plugins
from mayuri.utils.lang import tl
from pyrogram import Client, enums
from pyrogram.errors import FloodWait
from tzlocal import get_localzone

class Mayuri(Client):
	def __init__(self):
		name = self.__class__.__name__.lower()
		if BOT_SESSION:
			super().__init__(
				name,
				session_string=BOT_SESSION,
				api_id=API_ID,
				api_hash= API_HASH,
				workers=WORKERS,
				plugins=dict(
					root=f"{name}.plugins"
				),
				sleep_threshold=180
			)
		else:
			super().__init__(
				name,
				bot_token=BOT_TOKEN,
				api_id=API_ID,
				api_hash= API_HASH,
				workers=WORKERS,
				plugins=dict(
					root=f"{name}.plugins"
				),
				sleep_threshold=180
			)

	async def start(self):
		await super().start()
		scheduler.add_job(self.adminlist_watcher, "interval", seconds=21600) # run once every 2 hours
		scheduler.add_job(self.deleted_account_watcher, "cron", hour=18) # run once everyday at 6pm server time
		scheduler.start()
		await init_help(list_all_plugins())
		print("---[Mayuri Services is Running...]---")

	async def stop(self, *args):
		await super().stop()
		print("---[Bye]---")
		print("---[Thankyou for using my bot...]---")

	async def deleted_account_watcher(self):
		next_time = datetime.fromtimestamp(int(time.time() + (3600*24)))
		tz = datetime.now(get_localzone()).strftime("%Z")
		next_clean = f"{next_time} {tz}"
		for chat in grsql.chat_list():
			if not chat.chat_name: # Clean only public group
				continue
			try:
				chat_members_count = await self.get_chat_members_count(chat.chat_id)
				if chat_members_count >= 4000:
					continue
				chat_members = self.get_chat_members(chat.chat_id)
			except FloodWait as e:
				await asyncio.sleep(e.value)
			except Exception as e:
				print(e)
			count = 0
			async for member in chat_members:
				try:
					if member.user.is_deleted and not asql.check_admin(chat.chat_id, member.user.id):
						count = count+1
						await self.ban_chat_member(chat.chat_id, member.user.id)
				except FloodWait as e:
					await asyncio.sleep(e.value)
				except Exception as e:
					print(e)
			if count > 0:
				await self.send_message(chat.chat_id,(await tl(chat.chat_id, "zombies_cleaned_schedule")).format(count,next_clean))
			else:
				await self.send_message(chat.chat_id, (await tl(chat.chat_id, "no_zombies_schedule")).format(next_clean))

	async def adminlist_watcher(self):
		for chat in grsql.chat_list():
			asql.remove_admin_list(chat.chat_id)
			try:
				all_admin = self.get_chat_members(chat.chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
			except FloodWait as e:
				await asyncio.sleep(e.value)
			async for admin in all_admin:
				await asql.add_admin_to_list(chat.chat_id,admin.user.id,admin.user.username)
