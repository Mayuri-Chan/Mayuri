import threading

from mayuri import OWNER, BASE, SESSION
from sqlalchemy import Column, Integer, String, UnicodeText

class Chat(BASE):
	__tablename__ = "chat_list"
	chat_id = Column(String(15), primary_key=True)

	def __init__(self,chat_id):
		self.chat_id = str(chat_id)

	def __repr__(self):
		return "<Global chat for %s>" % (self.chat_id)

class Gban(BASE):
	__tablename__ = "gban_list"
	user_id = Column(Integer, primary_key=True)
	reason = Column(UnicodeText)

	def __init__(self,user_id,reason):
		self.user_id = user_id
		self.reason = reason

	def __repr__(self):
		return "<Global ban for %s>" % (self.user_id)

class Gmute(BASE):
	__tablename__ = "gmute_list"
	user_id = Column(Integer, primary_key=True)
	reason = Column(UnicodeText)

	def __init__(self,user_id,reason):
		self.user_id = user_id
		self.reason = reason

	def __repr__(self):
		return "<Global mute for %s>" % (self.user_id)

Chat.__table__.create(checkfirst=True)
Gban.__table__.create(checkfirst=True)
Gmute.__table__.create(checkfirst=True)
CHAT_INSERTION_LOCK = threading.RLock()

def add_to_chatlist(chat_id):
	with CHAT_INSERTION_LOCK:
		chat_filt = Chat(chat_id)
		SESSION.merge(chat_filt)
		SESSION.commit()

def check_chatlist(chat_id):
	try:
		return SESSION.query(Chat).get(str(chat_id))
	finally:
		SESSION.close()

def get_chatlist():
	try:
		return SESSION.query(Chat).all()
	finally:
		SESSION.close()

def add_to_gban(user_id,reason):
	with CHAT_INSERTION_LOCK:
		prev = SESSION.query(Gban).get(user_id)
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		gban_filt = Gban(user_id,reason)
		SESSION.merge(gban_filt)
		SESSION.commit()

def check_gban(user_id):
	try:
		return SESSION.query(Gban).get(user_id)
	finally:
		SESSION.close()

def rm_from_gban(user_id):
	with CHAT_INSERTION_LOCK:
		curr = SESSION.query(Gmute).get(user_id)
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True

		else:
			SESSION.close()
			return False

def add_to_gmute(user_id,reason):
	with CHAT_INSERTION_LOCK:
		prev = SESSION.query(Gmute).get(user_id)
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		gban_filt = Gmute(user_id,reason)
		SESSION.merge(gban_filt)
		SESSION.commit()

def check_gmute(user_id):
	try:
		return SESSION.query(Gmute).get(user_id)
	finally:
		SESSION.close()

def rm_from_gmute(user_id):
	with CHAT_INSERTION_LOCK:
		curr = SESSION.query(Gmute).get(user_id)
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True

		else:
			SESSION.close()
			return False
