import threading

from mayuri import BASE, SESSION
from sqlalchemy import Column, BigInteger, UnicodeText

class AdminSet(BASE):
	__tablename__ = "admin_settings"
	chat_id = Column(UnicodeText, primary_key=True)
	last_sync = Column(UnicodeText)

	def __init__(self,chat_id,last_sync):
		self.chat_id = str(chat_id)
		self.last_sync = last_sync

	def __repr__(self):
		return "<Admin_settings for %s>" % (self.chat_id)

class AdminList(BASE):
	__tablename__ = "admin_list"
	chat_id = Column(UnicodeText, primary_key=True)
	user_id = Column(BigInteger, primary_key=True)
	username = Column(UnicodeText)

	def __init__(self,chat_id,user_id,username):
		self.chat_id = str(chat_id)
		self.user_id = str(user_id)
		self.username = username

	def __repr__(self):
		return "<Admin_list for %s>" % (self.chat_id)


AdminSet.__table__.create(checkfirst=True)
AdminList.__table__.create(checkfirst=True)
ADMINSET_INSERTION_LOCK = threading.RLock()

def get_last_sync(chat_id):
	with ADMINSET_INSERTION_LOCK:
		prev = SESSION.query(AdminSet).get((str(chat_id)))
		if prev:
			return prev
		SESSION.close()
		return 'NA'

def update_last_sync(chat_id,last_sync):
	with ADMINSET_INSERTION_LOCK:
		prev = SESSION.query(AdminSet).get((str(chat_id)))
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		adminset = AdminSet(str(chat_id),str(last_sync))
		SESSION.merge(adminset)
		SESSION.commit()
		SESSION.close()

async def add_admin_to_list(chat_id,user_id,user_name):
	with ADMINSET_INSERTION_LOCK:
		prev = SESSION.query(AdminList).get((str(chat_id), user_id))
		if prev:
			SESSION.close()
			return
		admin_list = AdminList(chat_id,user_id,user_name)
		SESSION.merge(admin_list)
		SESSION.commit()
		SESSION.close()

def remove_admin_list(chat_id):
	with ADMINSET_INSERTION_LOCK:
		data = SESSION.query(AdminList).filter(AdminList.chat_id == str(chat_id)).all()
		for admin in data:
			SESSION.delete(admin)
			SESSION.commit()
		SESSION.close()

def get_admin_list(chat_id):
	try:
		return SESSION.query(AdminList).filter(AdminList.chat_id == str(chat_id)).all()
	finally:
		SESSION.close()

def check_admin(chat_id,user_id):
	check = SESSION.query(AdminList).get((str(chat_id), user_id))
	if check:
		return True
	return False
