from mayuri import AddHandler
from mayuri.modules.disableable import disableable
from pyrogram import filters

__MODULE__ = "Sed"
__HELP__ = """
Modul ini digunakan untuk mengubah kata dalam suatu pesan
[Sed]
> `s/<kata asli>/<kata ganti>`
contoh :
> `s/anu/nganu`
Mengubah semua kata 'anu' menjadi 'nganu' didalam pesan yang dibalas
"""

@disableable
async def sed(client,message):
	text = (message.text).split('/')
	old_word = text[1]
	new_word = text[2]
	old_text = message.reply_to_message.text
	new_text = old_text.replace(old_word,new_word)
	await message.reply_to_message.reply_text(new_text)

AddHandler(sed,filters.reply & filters.regex('^s/(.*?)'))
