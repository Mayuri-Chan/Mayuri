import threading

from mayuri import BASE, SESSION
from sqlalchemy import Column, Integer, String, UnicodeText

class Blsticker(BASE):
	__tablename__ = "blsticker"
	chat_id = Column(String(15), primary_key=True)
	stickerid = Column(UnicodeText, primary_key=True)
	mode = Column(Integer)
	reason = Column(UnicodeText)
	duration = Column(String(15))

	def __init__(self,chat_id,stickerid,mode,reason,duration):
		self.chat_id = str(chat_id)
		self.stickerid = stickerid
		self.mode = mode
		self.reason = reason
		self.duration = duration

	def __repr__(self):
		return "<Blacklist Stickers '%s' for %s>" % (self.stickerid, self.chat_id)


Blsticker.__table__.create(checkfirst=True)

BLSTICKER_INSERTION_LOCK = threading.RLock()

def add_to_blsticker(chat_id,stickerid,mode,reason,duration):
	with BLSTICKER_INSERTION_LOCK:
		prev = SESSION.query(Blsticker).get((str(chat_id), stickerid))
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		Blsticker_filt = Blsticker(chat_id,stickerid,mode,reason,duration)

		SESSION.merge(Blsticker_filt)
		SESSION.commit()

def rm_from_blsticker(chat_id,stickerid):
	with BLSTICKER_INSERTION_LOCK:
		curr = SESSION.query(Blsticker).get((str(chat_id), stickerid))
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True

		else:
			SESSION.close()
			return False

def blsticker_list(chat_id):
	try:
		return SESSION.query(Blsticker).filter(Blsticker.chat_id == str(chat_id)).order_by(Blsticker.stickerid.asc()).all()
	finally:
		SESSION.close()

def check_sticker(chat_id, stickerid):
	curr = SESSION.query(Blsticker).get((str(chat_id), stickerid))
	if curr:
		return curr
	return False
