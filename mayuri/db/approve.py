import threading

from mayuri import BASE, SESSION
from sqlalchemy import Column, BigInteger, UnicodeText

class Approve(BASE):
	__tablename__ = "approve_list"
	chat_id = Column(UnicodeText, primary_key=True)
	user_id = Column(BigInteger, primary_key=True)

	def __init__(self,chat_id,user_id):
		self.chat_id = str(chat_id)
		self.user_id = user_id

	def __repr__(self):
		return "<Approve for %s>" % (self.user_id)


Approve.__table__.create(checkfirst=True)
APPROVE_INSERTION_LOCK = threading.RLock()

def add_to_approve(chat_id,user_id):
	with APPROVE_INSERTION_LOCK:
		prev = SESSION.query(Approve).get((str(chat_id),user_id))
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		gban_filt = Approve(chat_id,user_id)
		SESSION.merge(gban_filt)
		SESSION.commit()

def approve_list(chat_id):
	try:
		return SESSION.query(Approve).filter(Approve.chat_id == str(chat_id)).order_by(Approve.user_id.asc()).all()
	finally:
		SESSION.close()
	return False

def rm_from_approve(chat_id,user_id):
	with APPROVE_INSERTION_LOCK:
		curr = SESSION.query(Approve).get((str(chat_id),user_id))
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True

		else:
			SESSION.close()
			return False

def check_approve(chat_id,user_id):
	check = SESSION.query(Approve).get((str(chat_id), user_id))
	if check:
		return True
	return False
