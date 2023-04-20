import threading

from mayuri import BASE, SESSION
from sqlalchemy import Column, UnicodeText

class Settings(BASE):
	__tablename__ = "settings"
	name = Column(UnicodeText, primary_key=True)
	value = Column(UnicodeText)

	def __init__(self,name,value):
		self.name = name
		self.value = value

	def __repr__(self):
		return "<Settings for %s>" % (self.user_id)

Settings.__table__.create(checkfirst=True)
SETTINGS_INSERTION_LOCK = threading.RLock()

def update_settings(name,value):
	with SETTINGS_INSERTION_LOCK:
		prev = SESSION.query(Settings).get(name)
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		settings_filt = Settings(name,value)
		SESSION.merge(settings_filt)
		SESSION.commit()

def get_settings(name):
	with SETTINGS_INSERTION_LOCK:
		return SESSION.query(Settings).get(name)
