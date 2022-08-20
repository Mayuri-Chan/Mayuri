import threading
import time

from mayuri import BASE, SESSION
from sqlalchemy import Column, BigInteger, String, UnicodeText

class Chat(BASE):
	__tablename__ = "chat_list"
	chat_id = Column(UnicodeText)
	chat_name = Column(String(50), primary_key=True)

	def __init__(self,chat_id,chat_name):
		self.chat_id = str(chat_id)
		self.chat_name = str(chat_name)

	def __repr__(self):
		return "<Global chat for %s>" % (self.chat_id)

class Gban(BASE):
	__tablename__ = "gban_list"
	user_id = Column(BigInteger, primary_key=True)
	reason = Column(UnicodeText)
	until = Column(BigInteger)
	date = Column(BigInteger)

	def __init__(self,user_id,reason,until,date):
		self.user_id = user_id
		self.reason = reason
		self.until = until
		self.date = date

	def __repr__(self):
		return "<Global ban for %s>" % (self.user_id)

class Gmute(BASE):
	__tablename__ = "gmute_list"
	user_id = Column(BigInteger, primary_key=True)
	reason = Column(UnicodeText)
	until = Column(BigInteger)
	date = Column(BigInteger)

	def __init__(self,user_id,reason,until,date):
		self.user_id = user_id
		self.reason = reason
		self.until = until
		self.date = date

	def __repr__(self):
		return "<Global mute for %s>" % (self.user_id)

class Gdmute(BASE):
	__tablename__ = "gdmute_list"
	user_id = Column(BigInteger, primary_key=True)
	reason = Column(UnicodeText)
	until = Column(BigInteger)
	date = Column(BigInteger)

	def __init__(self,user_id,reason,until,date):
		self.user_id = user_id
		self.reason = reason
		self.until = until
		self.date = date

	def __repr__(self):
		return "<Global dmute for %s>" % (self.user_id)


Chat.__table__.create(checkfirst=True)
Gban.__table__.create(checkfirst=True)
Gmute.__table__.create(checkfirst=True)
Gdmute.__table__.create(checkfirst=True)
CHAT_INSERTION_LOCK = threading.RLock()

def add_chat(chat_id,chat_name):
	with CHAT_INSERTION_LOCK:
		prev = SESSION.query(Chat).get(str(chat_id))
		if prev and prev.chat_name != chat_name:
			SESSION.delete(prev)
			SESSION.commit()
		chat_filt = Chat(chat_id,chat_name)
		SESSION.merge(chat_filt)
		SESSION.commit()

def check_chat(chat_id):
	try:
		prev = SESSION.query(Chat).get(str(chat_id))
		if prev:
			return prev
		return False
	finally:
		SESSION.close()
	return False

def chat_list():
	try:
		return SESSION.query(Chat).all()
	finally:
		SESSION.close()

def add_to_gban(user_id,reason,until):
	with CHAT_INSERTION_LOCK:
		prev = SESSION.query(Gban).get(user_id)
		if prev:
			if (until != 0 and prev.until == 0):
				return False
			SESSION.delete(prev)
			SESSION.commit()

		gban_filt = Gban(user_id,reason,until,time.time())
		SESSION.merge(gban_filt)
		SESSION.commit()
		return True

def check_gban(user_id):
	try:
		return SESSION.query(Gban).get(user_id)
	finally:
		SESSION.close()
	return False

def rm_from_gban(user_id):
	with CHAT_INSERTION_LOCK:
		curr = SESSION.query(Gban).get(user_id)
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True

		else:
			SESSION.close()
			return False

def add_to_gmute(user_id,reason,until):
	with CHAT_INSERTION_LOCK:
		prev = SESSION.query(Gmute).get(user_id)
		if prev:
			if (until != 0 and prev.until == 0):
				return False
			SESSION.delete(prev)
			SESSION.commit()

		gban_filt = Gmute(user_id,reason,until,time.time())
		SESSION.merge(gban_filt)
		SESSION.commit()
		return True

def check_gmute(user_id):
	try:
		return SESSION.query(Gmute).get(user_id)
	finally:
		SESSION.close()
	return False

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

def add_to_gdmute(user_id,reason,until):
	with CHAT_INSERTION_LOCK:
		prev = SESSION.query(Gdmute).get(user_id)
		if prev:
			if (until != 0 and prev.until == 0):
				return False
			if prev.until > until:
				return False
			SESSION.delete(prev)
			SESSION.commit()

		gban_filt = Gdmute(user_id,reason,until,time.time())
		SESSION.merge(gban_filt)
		SESSION.commit()
		return True

def check_gdmute(user_id):
	try:
		return SESSION.query(Gdmute).get(user_id)
	finally:
		SESSION.close()
	return False

def rm_from_gdmute(user_id):
	with CHAT_INSERTION_LOCK:
		curr = SESSION.query(Gdmute).get(user_id)
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True

		else:
			SESSION.close()
			return False
