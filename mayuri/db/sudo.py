import threading

from mayuri import BASE, SESSION
from sqlalchemy import Column, BigInteger

class Sudo(BASE):
	__tablename__ = "sudo_list"
	user_id = Column(BigInteger, primary_key=True)

	def __init__(self,user_id):
		self.user_id = str(user_id)

	def __repr__(self):
		return "<Sudo for %s>" % (self.user_id)


Sudo.__table__.create(checkfirst=True)
SUDO_INSERTION_LOCK = threading.RLock()

def add_to_sudo(user_id):
	with SUDO_INSERTION_LOCK:
		prev = SESSION.query(Sudo).get(user_id)
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		gban_filt = Sudo(user_id)
		SESSION.merge(gban_filt)
		SESSION.commit()

def sudo_list():
	try:
		return SESSION.query(Sudo).all()
	finally:
		SESSION.close()

def rm_from_sudo(user_id):
	with SUDO_INSERTION_LOCK:
		curr = SESSION.query(Sudo).get(user_id)
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True
		SESSION.close()
		return False

def check_sudo(user_id):
	with SUDO_INSERTION_LOCK:
		find = SESSION.query(Sudo).get(user_id)
		if find:
			return True
		return False
