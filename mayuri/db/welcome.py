import threading

from mayuri import BASE, SESSION
from sqlalchemy import Column, BigInteger, Boolean, UnicodeText

class Welcome(BASE):
	__tablename__ = "welcome_settings"
	chat_id = Column(BigInteger, primary_key=True)
	text = Column(UnicodeText)
	thread_id = Column(BigInteger)
	enable = Column(Boolean)
	clean_service = Column(Boolean)

	def __init__(self,chat_id,text,thread_id,enable,clean_service):
		self.chat_id = str(chat_id)
		self.text = text
		self.thread_id = thread_id
		self.enable = enable
		self.clean_service = clean_service

	def __repr__(self):
		return "<Welcome for %s>" % (self.chat_id)


Welcome.__table__.create(checkfirst=True)
WELCOME_INSERTION_LOCK = threading.RLock()

def set_welcome(chat_id,text,thread_id,enable,clean_service):
	with WELCOME_INSERTION_LOCK:
		prev = SESSION.query(Welcome).get(chat_id)
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		welcome_filt = Welcome(chat_id,text,thread_id,enable,clean_service)
		SESSION.merge(welcome_filt)
		SESSION.commit()

def get_welcome(chat_id):
	with WELCOME_INSERTION_LOCK:
		find = SESSION.query(Welcome).get(chat_id)
		if find:
			return find
		return False
