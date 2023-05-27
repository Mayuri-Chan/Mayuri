from time import time
from typing import Union

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

def time_left(seconds):
	now = time()
	seconds = seconds - now
	hour = seconds // 3600
	seconds %= 3600
	minutes = seconds // 60
	seconds %= 60

	return "%02d:%02d:%02d" % (hour, minutes, seconds)

def usec() -> int:
    """Returns the current time in microseconds since the Unix epoch."""

    return int(time() * 1000000)

def format_duration_us(t_us: Union[int, float]) -> str:
    """Formats the given microsecond duration as a string."""

    t_us = int(t_us)

    t_ms = t_us / 1000
    t_s = t_ms / 1000
    t_m = t_s / 60
    t_h = t_m / 60
    t_d = t_h / 24

    if t_d >= 1:
        rem_h = t_h % 24
        return "%dd %dh" % (t_d, rem_h)

    if t_h >= 1:
        rem_m = t_m % 60
        return "%dh %dm" % (t_h, rem_m)

    if t_m >= 1:
        rem_s = t_s % 60
        return "%dm %ds" % (t_m, rem_s)

    if t_s >= 1:
        return "%d sec" % t_s

    if t_ms >= 1:
        return "%d ms" % t_ms

    return "%d μs" % t_us
