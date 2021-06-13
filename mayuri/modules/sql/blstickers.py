import threading

from mayuri import OWNER, BASE, SESSION
from sqlalchemy import Column, Integer, String, UnicodeText

class Blstickers(BASE):
	__tablename__ = "blstickers"
	chat_id = Column(String(15), primary_key=True)
	stickerid = Column(UnicodeText, primary_key=True)
	mode = Column(Integer)
	time = Column(String(15))

	def __init__(self,chat_id,stickerid,mode,time):
		self.chat_id = str(chat_id)
		self.stickerid = stickerid
		self.mode = mode
		self.time = time

	def __repr__(self):
		return "<Blacklist Stickers '%s' for %s>" % (self.stickerid, self.chat_id)

Blstickers.__table__.create(checkfirst=True)

BLSTICKERS_INSERTION_LOCK = threading.RLock()

def add_to_blstickers(chat_id,stickerid,mode,time):
	with BLSTICKERS_INSERTION_LOCK:
		prev = SESSION.query(Blstickers).get((str(chat_id), stickerid))
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		Blstickers_filt = Blstickers(chat_id,stickerid,mode,time)

		SESSION.merge(Blstickers_filt)
		SESSION.commit()

def rm_from_blstickers(chat_id,stickerid):
	with BLSTICKERS_INSERTION_LOCK:
		curr = SESSION.query(Blstickers).get((str(chat_id), stickerid))
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True

		else:
			SESSION.close()
			return False

def blstickers_list(chat_id):
	try:
		return SESSION.query(Blstickers).filter(Blstickers.chat_id == str(chat_id)).order_by(Blstickers.stickerid.asc()).all()
	finally:
		SESSION.close()
