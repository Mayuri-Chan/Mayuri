import sys
from mayuri import bot, Command, OWNER
from pyrogram import filters, __version__
from pyrogram.handlers import MessageHandler

@bot.on_message((filters.command("alive", Command) | filters.command("on", Command)) & filters.user(OWNER))
async def alive(client, message):
	alive_text = "Bot services is running...\n----------------------------------\n•  ⚙️ Pyrogram    : v{}\n•  🐍 Python         : v{}\n----------------------------------".format(__version__,sys.version.split(' ')[0])
	await message.reply_text(alive_text)

