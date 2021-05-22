from mayuri import AddHandler
from mayuri.modules.disableable import disableable
from pyrogram import filters
from re import IGNORECASE, I, match, sub
from sre_constants import error as sre_err

__MODULE__ = "Sed"
__HELP__ = """
Modul ini digunakan untuk mengubah kata dalam suatu pesan
[Sed]
> `s/<kata asli>/<kata ganti>`
contoh :
> `s/anu/nganu`
Mengubah semua kata 'anu' menjadi 'nganu' didalam pesan yang dibalas
"""

DELIMITERS = ("/", ":", "|", "_")

def separate_sed(sed_string):
	if (
		len(sed_string) > 2
		and sed_string[1] in DELIMITERS
		and sed_string.count(sed_string[1]) >= 2
	):
		delim = sed_string[1]
		start = counter = 2
		while counter < len(sed_string):
			if sed_string[counter] == '\\':
				counter += 1

			elif sed_string[counter] == delim:
				replace = sed_string[start:counter]
				counter += 1
				start = counter
				break

			counter += 1

		else:
			return None

		while counter < len(sed_string):
			if (
				sed_string[counter] == '\\'
				and counter + 1 < len(sed_string)
				and sed_string[counter + 1] == delim
			):
				sed_string = sed_string[:counter] + sed_string[counter + 1 :]

			elif sed_string[counter] == delim:
				replace_with = sed_string[start:counter]
				counter += 1
				break

			counter += 1
		else:
			return replace, sed_string[start:], ''

		flags = ''
		if counter < len(sed_string):
			flags = sed_string[counter:]
		return replace, replace_with, flags.lower()
	return None


@disableable
async def sed(client,message):
	"""For sed command, use sed on Telegram."""
	sed_result = separate_sed(message.text or message.caption)
	textx = message.reply_to_message
	if sed_result:
		if textx:
			to_fix = textx.text
		else:
			return await message.reply_text(
				"`Master, I don't have brains. Well you too don't I guess.`"
			)

		repl, repl_with, flags = sed_result

		if not repl:
			return await message.reply_text(
				"`Master, I don't have brains. Well you too don't I guess.`"
			)

		try:
			check = match(repl, to_fix, flags=IGNORECASE)
			if check and check.group(0).lower() == to_fix.lower():
				return await message.reply_text("`Boi!, that's a reply. Don't use sed`")

			if "i" in flags and "g" in flags:
				text = sub(repl, repl_with, to_fix, flags=I).strip()
			elif "i" in flags:
				text = sub(repl, repl_with, to_fix, count=1, flags=I).strip()
			elif "g" in flags:
				text = sub(repl, repl_with, to_fix).strip()
			else:
				text = sub(repl, repl_with, to_fix, count=1).strip()
		except sre_err:
			return await message.reply_text("B O I! [Learn Regex](https://regexone.com)")
		if text:
			await message.reply_text(text)

AddHandler(sed,filters.reply & filters.regex('^s/(.*?)'))
