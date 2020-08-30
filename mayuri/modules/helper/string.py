import re

from pyrogram.types import InlineKeyboardButton

BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\(buttonurl:(?:/{0,2})(.+?)(:same)?\))")

def parse_button(text):
	markdown_note = text
	prev = 0
	note_data = ""
	buttons = []
	for match in BTN_URL_REGEX.finditer(markdown_note):
		# Check if btnurl is escaped
		n_escapes = 0
		to_check = match.start(1) - 1
		while to_check > 0 and markdown_note[to_check] == "\\":
			n_escapes += 1
			to_check -= 1
 
		# if even, not escaped -> create button
		if n_escapes % 2 == 0:
			# create a thruple with button label, url, and newline status
			buttons.append((match.group(2), match.group(3), bool(match.group(4))))
			note_data += markdown_note[prev:match.start(1)]
			prev = match.end(1)
		# if odd, escaped -> move along
		else:
			note_data += markdown_note[prev:to_check]
			prev = match.start(1) - 1
	else:
		note_data += markdown_note[prev:]

	return note_data, buttons


def build_keyboard(buttons):
	keyb = []
	for btn in buttons:
		if btn[-1] and keyb:
			keyb[-1].append(InlineKeyboardButton(btn[0], url=btn[1]))
		else:
			keyb.append([InlineKeyboardButton(btn[0], url=btn[1])])

	return keyb
