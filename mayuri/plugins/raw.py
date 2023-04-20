import ast
from mayuri.db import settings as sql
from mayuri.mayuri import Mayuri
from pyrogram import raw

@Mayuri.on_raw_update()
async def _raw(c,u,_,__):
	state = sql.get_settings("state")
	if not state:
		state = await c.invoke(raw.functions.updates.GetState())
		value = {"pts": state.pts, "qts": state.qts, "date": state.date}
		sql.update_settings("state", str(value))
		return
	value = ast.literal_eval(state.value)
	pts = value["pts"]
	date = value["date"]
	qts = value["qts"]
	new_pts = None
	new_date = None
	new_qts = None
	if hasattr(u, "pts"):
		new_pts = u.pts
	if hasattr(u, "date"):
		new_date = u.date
	if hasattr(u, "qts"):
		new_qts = u.qts
	if not new_pts and not new_date and not new_qts:
		return
	value = {'pts': new_pts or pts, 'qts': new_qts or qts, 'date': new_date or date}
	sql.update_settings("state",str(value))
