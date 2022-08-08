import threading

from mayuri import BASE, SESSION
from sqlalchemy import Column, Integer, UnicodeText

class Filters(BASE):
	__tablename__ = "filters"
	chat_id = Column(UnicodeText, primary_key=True)
	name = Column(UnicodeText, primary_key=True)
	value = Column(UnicodeText)
	document = Column(UnicodeText)
	filter_type = Column(Integer)
	document_type = Column(Integer)

	def __init__(self,chat_id,name,value,document,filter_type,document_type):
		self.chat_id = str(chat_id)
		self.name = name
		self.value = value
		self.document = document
		self.filter_type = filter_type
		self.document_type = document_type

	def __repr__(self):
		return "<Filter '%s' for %s>" % (self.trigger, self.chat_id)


Filters.__table__.create(checkfirst=True)
FILTERS_INSERTION_LOCK = threading.RLock()

def add_to_filter(chat_id,name,value,document,filter_type,document_type):
	with FILTERS_INSERTION_LOCK:
		prev = SESSION.query(Filters).get((str(chat_id), name))
		if prev:
			SESSION.delete(prev)
			SESSION.commit()

		filter_filt = Filters(chat_id,name,value,document,filter_type,document_type)

		SESSION.merge(filter_filt)
		SESSION.commit()

def rm_from_filter(chat_id,name):
	with FILTERS_INSERTION_LOCK:
		curr = SESSION.query(Filters).get((str(chat_id), name))
		if curr:
			SESSION.delete(curr)
			SESSION.commit()
			return True
		SESSION.close()
		return False

def filter_list(chat_id):
	try:
		return SESSION.query(Filters).filter(Filters.chat_id == str(chat_id)).order_by(Filters.name.asc()).all()
	finally:
		SESSION.close()
