from time import time

def create_time(time_raw):
	unit = time_raw[-1]
	time_val = time_raw[0:-1]
	now = time()
	result = ''
	if unit == "d":
		result = round(now + int(time_val) * 60 * 60 * 24)
	elif unit == "h":
		result = round(now + int(time_val) * 60 * 60 )
	elif unit == "m":
		result = round(now + int(time_val) * 60)
	elif unit == "s":
		if int(time_val) < 30:
			time_val = 40
		result = round(now + int(time_val))

	return result

def tl_time(time_raw):
	unit = time_raw[-1]
	time_val = time_raw[0:-1]
	result = ''
	if unit == "d":
		result = "{} Hari".format(time_val)
	elif unit == "h":
		result = "{} Jam".format(time_val)
	elif unit == "m":
		result = "{} Menit".format(time_val)
	elif unit == "s":
		if int(time_val) < 30:
			time_val = 40
		result = "{} Detik".format(time_val)
	return result
