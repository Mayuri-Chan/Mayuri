import re

from __main__ import HELP_COMMANDS
from mayuri import bot, Command, AddHandler
from mayuri.modules.helper.misc import paginate_modules

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

HELP_STRINGS = f"""
Kamu dapat menggunakan {", ".join(Command)} untuk mengeksekusi perintah bot ini.
Perintah **Utama** yang tersedia:
 - /start: mendapatkan pesan start
 - /help: mendapatkan semua bantuan
"""

async def help_parser(client, chat_id, text, keyboard=None):
	if not keyboard:
		keyboard = InlineKeyboardMarkup(paginate_modules(0, HELP_COMMANDS, "help"))
	await client.send_message(chat_id, text, parse_mode='markdown', reply_markup=keyboard)

async def help_command(client, message):
	if message.chat.type != "private":
		keyboard = InlineKeyboardMarkup(
			[[InlineKeyboardButton(text="Bantuan", url=f"t.me/{(await client.get_me()).username}?start=help")]])
		await message.reply("Hubungi saya di PM.", reply_markup=keyboard)
		return
	await help_parser(client, message.chat.id, HELP_STRINGS)

async def help_button_callback(_, __, query):
	if re.match(r"help_", query.data):
		return True

help_button_create = filters.create(help_button_callback)

@bot.on_callback_query(help_button_create)
async def help_button(_client, query):
	mod_match = re.match(r"help_module\((.+?)\)", query.data)
	back_match = re.match(r"help_back", query.data)
	if mod_match:
		module = mod_match.group(1)
		text = "Ini adalah bantuan untuk modul **{}**:\n".format(HELP_COMMANDS[module].__MODULE__) \
			   + HELP_COMMANDS[module].__HELP__

		await query.message.edit(text=text,
								parse_mode='markdown',
								reply_markup=InlineKeyboardMarkup(
									[[InlineKeyboardButton(text="Back", callback_data="help_back")]]))

	elif back_match:
		await query.message.edit(text=HELP_STRINGS,
								reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELP_COMMANDS, "help")))

AddHandler(help_command,filters.command("help", Command))
