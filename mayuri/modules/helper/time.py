import time

def create_time(time_raw):
	unit = time_raw[-1]
	time_val = time_raw[0:-1]
	result = ''
	if unit == "d":
		result = round(time.time() + int(time_val) * 60 * 60 * 24)
	elif unit == "h":
		result = round(time.time() + int(time_val) * 60 * 60 )
	elif unit == "m":
		result = round(time.time() + int(time_val) * 60)
	elif unit == "s":
		result = round(time.time() + int(time_val))

	return result
