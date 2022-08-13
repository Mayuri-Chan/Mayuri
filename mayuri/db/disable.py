import threading

from mayuri import BASE, SESSION
from sqlalchemy import Column, UnicodeText

class Disable(BASE):
	__tablename__ = "disabled_list"
	chat_id = Column(UnicodeText, primary_key=True)
	cmd = Column(UnicodeText, primary_key=True)

	def __init__(self,chat_id,cmd):
		self.chat_id = str(chat_id)
		self.cmd = cmd

	def __repr__(self):
		return "<Disable '%s' for %s>" % (self.cmd, self.chat_id)


Disable.__table__.create(checkfirst=True)
DISABLE_INSERTION_LOCK = threading.RLock()

def add_to_disabled(chat_id,cmd):
	with DISABLE_INSERTION_LOCK:
		prev = SESSION.query(Disable).get((str(chat_id), cmd))
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		disabled_filt = Disable(chat_id,cmd)

		SESSION.merge(disabled_filt)
		SESSION.commit()

def rm_from_disabled(chat_id,cmd):
	with DISABLE_INSERTION_LOCK:
		curr = SESSION.query(Disable).get((str(chat_id), cmd))
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True
		SESSION.close()
		return False

def disabled_list(chat_id):
	try:
		return SESSION.query(Disable).filter(Disable.chat_id == str(chat_id)).order_by(Disable.cmd.asc()).all()
	finally:
		SESSION.close()

def check_disabled(chat_id,cmd):
	curr = SESSION.query(Disable).get((str(chat_id), cmd))
	if curr:
		return True
	return False
