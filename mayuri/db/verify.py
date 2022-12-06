import threading

from mayuri import BASE, SESSION
from sqlalchemy import Column, BigInteger, Boolean, UnicodeText

class Verify(BASE):
	__tablename__ = "verify_list"
	verify_id = Column(UnicodeText, primary_key=True)
	chat_id = Column(BigInteger)
	user_id = Column(BigInteger)
	captcha = Column(BigInteger)
	is_mute = Column(Boolean)
	msg_id = Column(BigInteger)
	time = Column(BigInteger)

	def __init__(self,verify_id,chat_id,user_id,captcha,is_mute,msg_id,time):
		self.verify_id = verify_id
		self.chat_id = chat_id
		self.user_id = user_id
		self.captcha = captcha
		self.is_mute = is_mute
		self.msg_id = msg_id
		self.time = time

	def __repr__(self):
		return "<Verify for %s>" % (self.user_id)


Verify.__table__.create(checkfirst=True)
VERIFY_INSERTION_LOCK = threading.RLock()

def add_to_verify(verify_id,chat_id,user_id,captcha,is_mute,msg_id,time):
	with VERIFY_INSERTION_LOCK:
		prev = SESSION.query(Verify).get(verify_id)
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		verify_filt = Verify(verify_id,chat_id,user_id,captcha,is_mute,msg_id,time)
		SESSION.merge(verify_filt)
		SESSION.commit()


def rm_from_verify(verify_id):
	with VERIFY_INSERTION_LOCK:
		curr = SESSION.query(Verify).get(verify_id)
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True
		SESSION.close()
		return False


def get_captcha(verify_id):
	with VERIFY_INSERTION_LOCK:
		return SESSION.query(Verify).get(verify_id)

def get_all_captcha():
	with VERIFY_INSERTION_LOCK:
		return SESSION.query(Verify).all()

def check_verify(chat_id,user_id):
	with VERIFY_INSERTION_LOCK:
		return SESSION.query(Verify).filter(Verify.chat_id==chat_id).filter(Verify.user_id==user_id).all()
