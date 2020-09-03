import threading

from mayuri import OWNER, BASE, SESSION
from sqlalchemy import Column, Integer, String, UnicodeText

class Blacklist(BASE):
	__tablename__ = "blacklist"
	chat_id = Column(String(15), primary_key=True)
	trigger = Column(UnicodeText, primary_key=True)
	mode = Column(Integer)
	time = Column(String(15))

	def __init__(self,chat_id,trigger,mode,time):
		self.chat_id = str(chat_id)
		self.trigger = trigger
		self.mode = mode
		self.time = time

	def __repr__(self):
		return "<Anti Ubot '%s' for %s>" % (self.trigger, self.chat_id)

Blacklist.__table__.create(checkfirst=True)

BLACKLIST_INSERTION_LOCK = threading.RLock()

def add_to_blacklist(chat_id,trigger,mode,time):
	with BLACKLIST_INSERTION_LOCK:
		prev = SESSION.query(Blacklist).get((str(chat_id), trigger))
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		blacklist_filt = Blacklist(chat_id,trigger,mode,time)

		SESSION.merge(blacklist_filt)
		SESSION.commit()

def rm_from_blacklist(chat_id,trigger):
	with BLACKLIST_INSERTION_LOCK:
		curr = SESSION.query(Blacklist).get((str(chat_id), trigger))
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True

		else:
			SESSION.close()
			return False

def blacklist_list(chat_id):
	try:
		return SESSION.query(Blacklist).filter(Blacklist.chat_id == str(chat_id)).order_by(Blacklist.trigger.asc()).all()
	finally:
		SESSION.close()
