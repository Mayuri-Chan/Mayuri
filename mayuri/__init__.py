import os

from functools import wraps

from pyrogram import Client
from pyrogram.handlers import MessageHandler

# Postgresql
import threading

from sqlalchemy import create_engine, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import func, distinct, Column, String, UnicodeText, Integer

Command = os.environ.get("Command", "$ /").split()
if os.path.isfile('./mayuri/config.py'):
	from mayuri.config import Config
	API_ID = Config.API_ID
	API_HASH = Config.API_HASH
	BOT_SESSION = Config.BOT_SESSION
	TOKEN = Config.TOKEN
	OWNER = Config.OWNER
	DATABASE_URL = Config.DATABASE_URL
	log_chat = Config.log_chat
else:
	try:
		API_ID = os.environ.get(API_ID, None)
	except ValueError:
		raise Exception('You must set API_ID')

	try:
		API_HASH = os.environ.get(API_HASH, None)
	except ValueError:
		raise Exception('You must set API_HASH')

	isBotSession = False
	try:
		BOT_SESSION = os.environ.get(BOT_SESSION, None)
		isBotSession = True
	except ValueError:
		isBotSession = False

	if isBotSession == False:
		try:
			Token = os.environ.get(TOKEN, None)
		except ValueError:
			raise Exception('You must set BOT_SESSION or TOKEN')

	try:
		OWNER = os.environ.get(OWNER, None)
	except ValueError:
		raise Exception('You must set OWNER')

	try:
		DATABASE_URL = os.environ.get(DATABASE_URL, None)
	except ValueError:
		raise Exception('You must set DATABASE_URL')

	log_chat = os.environ.get(log_chat, None)

if BOT_SESSION != '':
	bot = Client(
		BOT_SESSION,
		api_id=API_ID,
		api_hash=API_HASH
	)
else:
	bot = Client(
		"my_bot",
		api_id=API_ID,
		api_hash=API_HASH,
		bot_token=TOKEN
	)

# Postgresql
def mulaisql() -> scoped_session:
	global DB_AVAIABLE
	engine = create_engine(DATABASE_URL, client_encoding="utf8")
	BASE.metadata.bind = engine
	try:
		BASE.metadata.create_all(engine)
	except exc.OperationalError:
		DB_AVAIABLE = False
		return False
	DB_AVAIABLE = True
	return scoped_session(sessionmaker(bind=engine, autoflush=False))

BASE = declarative_base()
SESSION = mulaisql()
DisableAbleLs = []
SUDO = []

def AddHandler(func,filt):
	my_handler = MessageHandler(func,filt)
	bot.add_handler(my_handler)

async def adminlist(client,chat_id):
    all = client.iter_chat_members(chat_id, filter="administrators")
    admin = []
    async for a in all:
        admin.append(a.user.id)
    return admin

def admin(func):
	wraps(func)
	async def decorator(client,message):
		chat_id = message.chat.id
		all_admin = await adminlist(client,chat_id)
		if message.from_user.id in all_admin:
			await func(client,message)
		else:
			await message.reply_text("Anda bukan admin!")
	return decorator

def sudo(func):
	wraps(func)
	async def decorator(client,message):
		user_id = message.from_user.id
		if user_id not in OWNER and user_id not in SUDO:
			return
		else:
			await func(client,message)
	return decorator
