import threading

from mayuri import OWNER, BASE, SESSION
from sqlalchemy import Column, Integer, String, UnicodeText

class Blpack(BASE):
	__tablename__ = "blpack"
	chat_id = Column(String(15), primary_key=True)
	packname = Column(UnicodeText, primary_key=True)
	mode = Column(Integer)
	time = Column(String(15))

	def __init__(self,chat_id,packname,mode,time):
		self.chat_id = str(chat_id)
		self.packname = packname
		self.mode = mode
		self.time = time

	def __repr__(self):
		return "<Blacklist Stickers '%s' for %s>" % (self.packname, self.chat_id)

Blpack.__table__.create(checkfirst=True)

BLPACK_INSERTION_LOCK = threading.RLock()

def add_to_blpack(chat_id,packname,mode,time):
	with BLPACK_INSERTION_LOCK:
		prev = SESSION.query(Blpack).get((str(chat_id), packname))
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		Blpack_filt = Blpack(chat_id,packname,mode,time)

		SESSION.merge(Blpack_filt)
		SESSION.commit()

def rm_from_blpack(chat_id,packname):
	with BLPACK_INSERTION_LOCK:
		curr = SESSION.query(Blpack).get((str(chat_id), packname))
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True

		else:
			SESSION.close()
			return False

def blpack_list(chat_id):
	try:
		return SESSION.query(Blpack).filter(Blpack.chat_id == str(chat_id)).order_by(Blpack.packname.asc()).all()
	finally:
		SESSION.close()
