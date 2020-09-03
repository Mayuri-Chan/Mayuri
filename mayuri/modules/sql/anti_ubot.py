import threading

from mayuri import OWNER, BASE, SESSION
from sqlalchemy import Column, Integer, String

class AntiUbot(BASE):
	__tablename__ = "anti_ubot"
	chat_id = Column(String(15), primary_key=True)
	command = Column(String(25), primary_key=True)
	mode = Column(Integer)
	time = Column(String(15))

	def __init__(self,chat_id,command,mode,time):
		self.chat_id = str(chat_id)
		self.command = command
		self.mode = mode
		self.time = time

	def __repr__(self):
		return "<Anti Ubot '%s' for %s>" % (self.command, self.chat_id)

AntiUbot.__table__.create(checkfirst=True)

ANTIUBOT_INSERTION_LOCK = threading.RLock()

def add_to_antiubot(chat_id,command,mode,time):
	with ANTIUBOT_INSERTION_LOCK:
		prev = SESSION.query(AntiUbot).get((str(chat_id), command))
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		antiubot_filt = AntiUbot(chat_id,command,mode,time)

		SESSION.merge(antiubot_filt)
		SESSION.commit()

def rm_from_antiubot(chat_id,command):
	with ANTIUBOT_INSERTION_LOCK:
		curr = SESSION.query(AntiUbot).get((str(chat_id), command))
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True

		else:
			SESSION.close()
			return False

def check_antiubot(chat_id,command):
	try:
		return SESSION.query(AntiUbot).get((str(chat_id), command))
	finally:
		SESSION.close()

def antiubot_list(chat_id):
	try:
		return SESSION.query(AntiUbot).filter(AntiUbot.chat_id == str(chat_id)).order_by(AntiUbot.command.asc()).all()
	finally:
		SESSION.close()
