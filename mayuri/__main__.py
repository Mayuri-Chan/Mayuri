import pyrogram
import importlib

from mayuri import bot, Command, OWNER
from mayuri.modules import ALL_MODULES
from mayuri.modules.helper.misc import paginate_modules

from pyrogram import filters, idle
from pyrogram.handlers import MessageHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

print("Mayuri is Starting...")

HELP_COMMANDS = {}

bot.start()

@bot.on_message(filters.command("start", Command))
async def start(client,message):
	if message.chat.type != "private":
		await message.reply("Hubungi saya di PM.")
		return

	HELP_STRINGS = f"""
	Kamu dapat menggunakan {", ".join(Command)} untuk mengeksekusi perintah bot ini.
	Perintah **Utama** yang tersedia:
	 - /start: mendapatkan pesan start
	 - /help: mendapatkan semua bantuan
	"""
	text = (message.text).split()
	if len(text) > 1 and text[1] == 'help':
		keyboard = None
		if not keyboard:
			keyboard = InlineKeyboardMarkup(paginate_modules(0, HELP_COMMANDS, "help"))
		await message.reply_text(HELP_STRINGS, parse_mode='markdown', reply_markup=keyboard)
	else:
		keyboard = InlineKeyboardMarkup(
			[[InlineKeyboardButton(text="Bantuan", url=f"t.me/{(await client.get_me()).username}?start=help")]])
		await message.reply_text("hello!\nThis bot is under development.\nYou can contact my master [here](tg://user?id={})\n\nPowered by [Pyrogram v{}](https://pyrogram.org)".format(OWNER[0],pyrogram.__version__),reply_markup=keyboard)

print("Loading modules...")

for module_name in ALL_MODULES:
	imported_module = importlib.import_module("mayuri.modules." + module_name)
	if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
		imported_module.__MODULE__ = imported_module.__MODULE__
	if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
		if not imported_module.__MODULE__.lower() in HELP_COMMANDS:
			HELP_COMMANDS[imported_module.__MODULE__.lower()] = imported_module
		else:
			raise Exception("Can't have two modules with the same name! Please change one")
	if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
		HELP_COMMANDS[imported_module.__MODULE__.lower()] = imported_module
	importlib.reload(imported_module)

print("----------------------------------------------------------------")
print(" Loaded Modules : ["+", ".join(ALL_MODULES)+"]")
print("----------------------------------------------------------------")
print()
print(" ---[Mayuri Services is Running...]---")
print()
print(" Thanks for using my bot :)")
print()

idle()
