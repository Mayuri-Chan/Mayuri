import asyncio
import colorlog
import importlib
import logging
import time
from async_pymongo import AsyncClient
from apscheduler import RunState
from apscheduler.schedulers.async_ import AsyncScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from mayuri import config, init_help
from mayuri.plugins import list_all_plugins
from pyrogram import Client, enums, raw
from pyrogram.errors import FloodWait, RPCError
from time import time
from tzlocal import get_localzone

log = logging.getLogger("Mayuri")

class Mayuri(Client):
	def __init__(self):
		name = self.__class__.__name__.lower()
		conn = AsyncClient(config['bot']['DATABASE_URL'])
		super().__init__(
			"mayuri_sessions",
			bot_token=config['bot']['BOT_TOKEN'],
			api_id=config['telegram']['API_ID'],
			api_hash=config['telegram']['API_HASH'],
			mongodb=dict(connection=conn, remove_peers=False),
			workers=config['bot']['WORKERS'],
			plugins=dict(
				root=f"{name}.plugins"
			),
			sleep_threshold=180
		)
		self.config = config
		self.db = conn["mayuri"]
		self.log = log
		self.scheduler = AsyncScheduler()

	async def start(self):
		self._setup_log()
		self.log.info("---[Starting bot...]---")
		await super().start()
		await self.catch_up()
		await self.start_scheduler()
		await init_help(list_all_plugins())
		self.log.info("---[Mayuri Services is Running...]---")

	async def stop(self, *args):
		self.log.info("---[Saving state...]---")
		db = self.db['bot_settings']
		state = await self.invoke(raw.functions.updates.GetState())
		value = {'pts': state.pts, 'qts': state.qts, 'date': state.date}
		await db.update_one({'name': 'state'}, {"$set": {'value': value}})
		await super().stop()
		self.log.info("---[Bye]---")
		self.log.info("---[Thankyou for using my bot...]---")

	def _setup_log(self):
		"""Configures logging"""
		level = logging.INFO
		logging.root.setLevel(level)

		# Color log config
		log_color: bool = True

		file_format = "[ %(asctime)s: %(levelname)-8s ] %(name)-15s - %(message)s"
		logfile = logging.FileHandler("Mayuri.log")
		formatter = logging.Formatter(file_format, datefmt="%H:%M:%S")
		logfile.setFormatter(formatter)
		logfile.setLevel(level)

		if log_color:
			formatter = colorlog.ColoredFormatter(
				"  %(log_color)s%(levelname)-8s%(reset)s  |  "
				"%(name)-15s  |  %(log_color)s%(message)s%(reset)s"
			)
		else:
			formatter = logging.Formatter("  %(levelname)-8s  |  %(name)-15s  |  %(message)s")
		stream = logging.StreamHandler()
		stream.setLevel(level)
		stream.setFormatter(formatter)

		root = logging.getLogger()
		root.setLevel(level)
		root.addHandler(stream)
		root.addHandler(logfile)

		# Logging necessary for selected libs
		logging.getLogger("pymongo").setLevel(logging.WARNING)
		logging.getLogger("pyrogram").setLevel(logging.ERROR)
		logging.getLogger("apscheduler").setLevel(logging.WARNING)

	async def catch_up(self):
		self.log.info("---[Recovering gaps...]---")
		while(True):
			db = self.db['bot_settings']
			state = await db.find_one({'name': 'state'})
			if not state:
				state = await self.invoke(raw.functions.updates.GetState())
				value = {'pts': state.pts, 'qts': state.qts, 'date': state.date}
				await db.insert_one({'name': 'state', 'value': value})
				break
			value = state['value']
			diff = await self.invoke(
					raw.functions.updates.GetDifference(
						pts=value['pts'],
						date=value['date'],
						qts=-1
					)
				)
			if isinstance(diff, raw.types.updates.DifferenceEmpty):
				new_value = {'pts': value['pts'], 'qts': value['qts'], 'date': diff.date}
				await db.update_one({'name': 'state'}, {"$set": {'value': new_value}})
				break
			elif isinstance(diff, raw.types.updates.DifferenceTooLong):
				new_value = {'pts': diff.pts, 'qts': value['qts'], 'date': diff.date}
				await db.update_one({'name': 'state'}, {"$set": {'value': new_value}})
				continue
			users = {u.id: u for u in diff.users}
			chats = {c.id: c for c in diff.chats}
			if isinstance(diff, raw.types.updates.DifferenceSlice):
				new_state = diff.intermediate_state
			else:
				new_state = diff.state
			for msg in diff.new_messages:
				self.dispatcher.updates_queue.put_nowait((
					raw.types.UpdateNewMessage(
						message=msg,
						pts=new_state.pts,
						pts_count=-1
					),
					users,
					chats
				))

			for update in diff.other_updates:
				self.dispatcher.updates_queue.put_nowait((update, users, chats))
			if isinstance(diff, raw.types.updates.Difference):
				break

	async def tl(self, chat_id, string):
		db = self.db["chat_settings"]
		check = await db.find_one({'chat_id': chat_id})
		if check and "lang" in check:
			lang = check["lang"]
		else:
			lang = "id"
		t = importlib.import_module("mayuri.lang."+lang)
		if string in t.text:
			return t.text[string]
		return (t.text['translation_not_found']).format(string)

	async def check_admin(self, chat_id, user_id):
		db = self.db["admin_list"]
		check = await db.find_one({"chat_id": chat_id})
		if check and user_id in check["list"]:
			return True
		return False

	async def check_approved(self, chat_id, user_id):
		db = self.db["chat_settings"]
		check = await db.find_one({"chat_id": chat_id})
		if check and "approved" in check and user_id in check["approved"]:
			return True
		return False

	async def check_sudo(self, user_id):
		db = self.db["bot_settings"]
		check = await db.find_one({'name': 'sudo_list'})
		if user_id == config['bot']['OWNER']:
			return True
		if check and user_id in check["list"]:
			return True
		return False

	async def start_scheduler(self):
		self.log.info("---[Starting scheduler...]---")
		# Initialize the scheduler
		await self.scheduler.__aenter__()

		# check if scheduler is already started
		if self.scheduler.state == RunState.stopped:
			# run every 2 hours
			await self.scheduler.add_schedule(self.adminlist_watcher, IntervalTrigger(seconds=21600))
			# run every 5 minutes
			await self.scheduler.add_schedule(self.captcha_timeout_watcher, IntervalTrigger(seconds=60*5))
			# run twice a week on monday and thursday at 6pm server time
			await self.scheduler.add_schedule(self.deleted_account_watcher, CronTrigger(day_of_week="mon,thu", hour=18))
			# Run the scheduler in background
			await self.scheduler.start_in_background()

	async def adminlist_watcher(self):
		db = self.db["admin_list"]
		chat_db = self.db["chat_list"]
		async for chat in chat_db.find():
			admin_list = []
			chat_id = chat["chat_id"]
			check = await db.find_one({'chat_id': chat_id})
			try:
				all_admin = self.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
			except FloodWait as e:
				await asyncio.sleep(e.value)
			except RPCError as e:
				self.log.warning(e)
				continue
			async for admin in all_admin:
				admin_list.append(admin.user.id)
			if check:
				for user_id in check["list"]:
					if user_id not in admin_list:
						await db.update_one({'chat_id': chat_id},{"$pull": {'list': user_id}})
			second_loop = False
			for user_id in admin_list:
				if check or second_loop:
					if second_loop:
						check = await db.find_one({'chat_id': chat_id})
					if user_id not in check["list"]:
						await db.update_one({'chat_id': chat_id},{"$push": {'list': user_id}})
				else:
					await db.update_one({'chat_id': chat_id},{"$push": {'list': user_id}}, upsert=True)
					second_loop = True

	async def captcha_timeout_watcher(self):
		db = self.db['captcha_list']
		now = time()
		async for data in db.find():
			if data['timeout'] <= now:
				try:
					if data['is_request']:
						await self.decline_chat_join_request(data['chat_id'], data['user_id'])
					else:
						await self.ban_chat_member(data['chat_id'], data['user_id'])
						await self.unban_chat_member(data['chat_id'], data['user_id'])
					msg = await self.get_messages(data['chat_id'], data['msg_id'])
					await msg.delete()
				except Exception:
					pass
				await db.delete_one({'verify_id': data['verify_id']})

	async def deleted_account_watcher(self):
		db = self.db["chat_list"]
		next_time = datetime.fromtimestamp(int(time.time() + (3600*24)))
		tz = datetime.now(get_localzone()).strftime("%Z")
		next_clean = f"{next_time} {tz}"
		async for chat in db.find():
			if not chat['chat_username']: # Clean only public group
				continue
			try:
				chat_members_count = await self.get_chat_members_count(chat['chat_id'])
				# Clean only group with less than 4k members
				# Because telegram limit how much user you can get if the group have ~4000 and more members
				if chat_members_count >= 4000:
					continue
				chat_members = self.get_chat_members(chat['chat_id'])
			except FloodWait as e:
				await asyncio.sleep(e.value)
			except Exception as e:
				print(e)
			count = 0
			async for member in chat_members:
				try:
					if member.user.is_deleted and not await self.check_admin(chat['chat_id'], member.user.id):
						count = count+1
						await self.ban_chat_member(chat['chat_id'], member.user.id)
				except FloodWait as e:
					await asyncio.sleep(e.value)
				except Exception as e:
					print(e)
			if count > 0:
				await self.send_message(chat['chat_id'],(await self.tl(chat['chat_id'], "zombies_cleaned_schedule")).format(count,next_clean))
