import asyncio
import time

from apscheduler import RunState
from apscheduler.schedulers.async_ import AsyncScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from mayuri import API_ID, API_HASH, BOT_SESSION, BOT_TOKEN, WORKERS, init_help
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
		self.scheduler = None

	async def start(self):
		await super().start()
		await self.start_scheduler()
		await init_help(list_all_plugins())
		print("---[Mayuri Services is Running...]---")

	async def stop(self, *args):
		await super().stop()
		print("---[Bye]---")
		print("---[Thankyou for using my bot...]---")

	async def start_scheduler(self):
		# Initialize the scheduler
		self.scheduler = AsyncScheduler()
		await self.scheduler.__aenter__()

		# check if scheduler is already started
		if self.scheduler.state == RunState.stopped:
			# run every 2 hours
			await self.scheduler.add_schedule(self.adminlist_watcher, IntervalTrigger(seconds=21600))
			# run every Monday and Thursday 6 pm server time
			await self.scheduler.add_schedule(self.deleted_account_watcher, CronTrigger(day_of_week="mon,thu", hour=18))
			# Run the scheduler in background
			await self.scheduler.start_in_background()

	async def deleted_account_watcher(self):
		if datetime.strftime("%a") == "Mon":
			next_time = datetime.fromtimestamp(int(time.time() + (3600*24*3)))
		else:
			next_time = datetime.fromtimestamp(int(time.time() + (3600*24*4)))
		tz = datetime.now(get_localzone()).strftime("%Z")
		next_clean = f"{next_time} {tz}"
		for chat in grsql.chat_list():
			if chat.chat_name == "None": # Clean only public group
				continue
			try:
				chat_members_count = await self.get_chat_members_count(chat.chat_id)
				if chat_members_count >= 3000:
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
