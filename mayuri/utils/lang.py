import importlib
from mayuri.db import lang as lang_db

async def tl(chat_id, string):
	check = lang_db.check_lang(chat_id)
	if check:
		lang = check.lang
	else:
		lang = "id"
	t = importlib.import_module("mayuri.lang."+lang)
	return t.text[string]
