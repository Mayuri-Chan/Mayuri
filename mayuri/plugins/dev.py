import inspect
import io
import os
import pyrofork
import re
import sys
import traceback
import uuid

from html import escape
from mayuri import PREFIX
from mayuri.mayuri import Mayuri
from mayuri.util.error import format_exception
from mayuri.util.filters import owner_only
from mayuri.util.time import format_duration_us, usec
from meval import meval
from pyrofork import filters
from typing import Any, Optional, Tuple

@Mayuri.on_message(filters.command("eval", PREFIX) & owner_only)
async def exec_eval(c,m):
	text = m.text.split(None,1)
	if not len(text) > 1:
		return
	code = text[1]
	out_buf = io.StringIO()
	async def _eval() -> Tuple[str, Optional[str]]:
		# Message sending helper for convenience
		async def send(*args: Any, **kwargs: Any) -> pyrofork.types.Message:
			return await m.reply(*args, **kwargs)

		# Print wrapper to capture output
		# We don't override sys.stdout to avoid interfering with other output
		def _print(*args: Any, **kwargs: Any) -> None:
			if "file" not in kwargs:
				kwargs["file"] = out_buf
				return print(*args, **kwargs)

		eval_vars = {
			# Contextual info
			"loop": c.loop,
			"client": c,
			"stdout": out_buf,
			"db": c.db,
			# Convenience aliases
			"c": c,
			"m": m,
			"msg": m,
			"message": m,
			"raw": pyrofork.raw,
			# Helper functions
			"send": send,
			"print": _print,
			# Built-in modules
			"inspect": inspect,
			"os": os,
			"re": re,
			"sys": sys,
			"traceback": traceback,
			# Third-party modules
			"pyrofork": pyrofork,
		}

		try:
			return "", await meval(code, globals(), **eval_vars)
		except Exception as e:  # skipcq: PYL-W0703
			# Find first traceback frame involving the snippet
			first_snip_idx = -1
			tb = traceback.extract_tb(e.__traceback__)
			for i, frame in enumerate(tb):
				if frame.filename == "<string>" or frame.filename.endswith("ast.py"):
					first_snip_idx = i
					break

			# Re-raise exception if it wasn't caused by the snippet
			if first_snip_idx == -1:
				raise e
			# Return formatted stripped traceback
			stripped_tb = tb[first_snip_idx:]
			formatted_tb = format_exception(e, tb=stripped_tb)
			return "⚠️ Error executing snippet\n\n", formatted_tb

	before = usec()
	prefix, result = await _eval()
	after = usec()

	# Always write result if no output has been collected thus far
	if not out_buf.getvalue() or result is not None:
		print(result, file=out_buf)

	el_us = after - before
	el_str = format_duration_us(el_us)

	out = out_buf.getvalue()
	# Strip only ONE final newline to compensate for our message formatting
	if out.endswith("\n"):
		out = out[:-1]

	result = f"""{prefix}<b>In:</b>
<pre language="python">{escape(code)}</pre>
<b>Out:</b>
<pre language="python">{escape(out)}</pre>
Time: {el_str}"""

	if len(result) > 4096:
		with io.BytesIO(str.encode(out)) as out_file:
			out_file.name = str(uuid.uuid4()).split("-")[0].upper() + ".TXT"
			caption = f"""{prefix}<b>In:</b>
<pre language="python">{escape(code)}</pre>

Time: {el_str}"""
			await m.reply_document(
				document=out_file, caption=caption, disable_notification=True,parse_mode=pyrofork.enums.parse_mode.ParseMode.HTML
			)
		return None

	await m.reply_text(
		result,
		parse_mode=pyrofork.enums.parse_mode.ParseMode.HTML,
	)
