from mayuri import AddHandler
from mayuri.modules.disableable import disableable
from pyrogram import filters

@disableable
async def sed(client,message):
	text = (message.text).split('/')
	old_word = text[1]
	new_word = text[2]
	old_text = message.reply_to_message.text
	new_text = old_text.replace(old_word,new_word)
	await message.reply_to_message.reply_text(new_text)

AddHandler(sed,filters.reply & filters.regex('^s/(.*?)'))
