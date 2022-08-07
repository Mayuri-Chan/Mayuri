import threading

from mayuri import BASE, SESSION
from sqlalchemy import Column, UnicodeText

class Lang(BASE):
	__tablename__ = "language"
	chat_id = Column(UnicodeText, primary_key=True)
	lang = Column(UnicodeText)

	def __init__(self, chat_id, lang):
		self.chat_id = str(chat_id)
		self.lang = lang

	def __repr__(self):
		return "<Lang for %s>" % (self.chat_id)


Lang.__table__.create(checkfirst=True)
LANG_INSERTION_LOCK = threading.RLock()

def check_lang(chat_id):
	with LANG_INSERTION_LOCK:
		find = SESSION.query(Lang).get(str(chat_id))
		if find:
			return find
		return False
