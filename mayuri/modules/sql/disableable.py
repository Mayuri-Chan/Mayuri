import threading

from mayuri import OWNER, BASE, SESSION
from sqlalchemy import Column, Integer, String, Boolean, UnicodeText, and_

class DisableAble(BASE):
	__tablename__ = "disableable_command"
	chat_id = Column(String(15), primary_key=True)
	command = Column(String(50), primary_key=True)

	def __init__(self,chat_id,command):
		self.chat_id = str(chat_id)
		self.command = command

	def __repr__(self):
		return "<disableable_command '%s' for %s>" % (self.command, self.chat_id)

DisableAble.__table__.create(checkfirst=True)
DISABLEABLE_INSERTION_LOCK = threading.RLock()

def add_to_disableable(chat_id,command):
	with DISABLEABLE_INSERTION_LOCK:

		disableable_filt = DisableAble(chat_id,command)

		SESSION.merge(disableable_filt)
		SESSION.commit()

def rm_from_disableable(chat_id,command):
	with DISABLEABLE_INSERTION_LOCK:
		curr = SESSION.query(DisableAble).get((str(chat_id), command))
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True

		else:
			SESSION.close()
			return False

def get_disableable(command):
	try:
		return SESSION.query(DisableAble).filter(DisableAble.command == str(command)).order_by(DisableAble.chat_id.asc()).all()
	finally:
		SESSION.close()

def check_disableable(chat_id,command):
	try:
		return SESSION.query(DisableAble).get((str(chat_id), command))
	finally:
		SESSION.close()