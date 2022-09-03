class Config(object):
	API_ID = "" # from my.telegram.org
	API_HASH = "" # from my.telegram.org
	# You don't need to fill both BOT_TOKEN and BOT_SESSION, just fill one of it
	# BOT_TOKEN : bot token from https://t.me/BotFather, recommended if you have persistent storage like vps
	# BOT_TOKEN : generate using string_session.py, recommended for ephemeral filesystems like heroku
	BOT_TOKEN = ""
	BOT_SESSION = ""
	OWNER = 864 # Your telegram id
	DATABASE_URL = "postgresql://postgres:password@localhost:5172/db" # Your database URI
	WORKERS = 6
	CUSTOM_PREFIXS = ['/', '$']
	LOG_CHAT = -1001233232 # required for global restrictions
	LOG_STICKER = -1001233232 # required for kang sticker
	USE_OCR = False # you need to install tesseract on your server to enable ocr
