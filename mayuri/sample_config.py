class Config(object):
	API_ID = "" # from my.telegram.org
	API_HASH = "" # from my.telegram.org
	# BOT_SESSION & TOKEN are optional if one of these already filled
	BOT_SESSION = "" # generate using session_maker.py
	TOKEN = "" # bot token from https://t.me/BotFather
	OWNER = [864824682] # Your telegram id, you can set more than one, use comma (,) for separator
	DATABASE_URL = "postgresql://postgres:password@localhost:5432/db" # Your database URI
	log_chat = -123456 # Dummy channel or groups for store kanged sticker
