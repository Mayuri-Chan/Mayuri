import sys
from mayuri import Command, OWNER, AddHandler
from mayuri.modules.sudo import sudo
from pyrogram import filters, __version__

__MODULE__ = "Alive"
__HELP__ = """
Module ini digunakan untuk menampilkan status bot.
[Alive]
> `/alive`
> `/on`
"""

@sudo
async def alive(client, message):
	alive_text = "Bot services is running...\n----------------------------------\n•  ⚙️ Pyrogram    : v{}\n•  🐍 Python         : v{}\n----------------------------------".format(__version__,sys.version.split(' ')[0])
	await message.reply_text(alive_text)

AddHandler(alive,(filters.command("alive", Command) | filters.command("on", Command)))