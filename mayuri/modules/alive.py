import sys
from mayuri import Command, OWNER, AddHandler
from pyrogram import filters, __version__

async def alive(client, message):
	alive_text = "Bot services is running...\n----------------------------------\n•  ⚙️ Pyrogram    : v{}\n•  🐍 Python         : v{}\n----------------------------------".format(__version__,sys.version.split(' ')[0])
	await message.reply_text(alive_text)

AddHandler(alive,(filters.command("alive", Command) | filters.command("on", Command)) & filters.user(OWNER))