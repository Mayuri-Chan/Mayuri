import colorlog
import importlib
import logging
import os
from async_pymongo import AsyncClient
from apscheduler import RunState
from apscheduler.schedulers.async_ import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger
from mayuri import config, init_help
from mayuri.plugins import list_all_plugins
from pyrogram import Client, enums, raw
from pyrogram.errors import FloodWait, RPCError

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
				await db.update_one({'name': 'state'}, {"$set": {'value': value}})
				break
			elif isinstance(diff, raw.types.updates.DifferenceTooLong):
				new_value = {'pts': diff.pts, 'qts': value['qts'], 'date': diff.date}
				await db.update_one({'name': 'state'}, {"$set": {'value': value}})
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
		return t.text[string]

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
						await db.update_one({'chat_id': chat_id},{"$pull": {'list': admin.user.id}})
			for user_id in admin_list:
				if check:
					if user_id not in check["list"]:
						await db.update_one({'chat_id': chat_id},{"$push": {'list': admin.user.id}})
				else:
					await db.update_one({'chat_id': chat_id},{"$push": {'list': admin.user.id}}, upsert=True)
