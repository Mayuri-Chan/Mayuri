import io
import os
import pyrogram
from async_pymongo import AsyncClient
from bson import json_util
from datetime import datetime

async def backup(c):
	db = c.db
	chat_id = c.config["backup"]["BACKUP_CHAT"]
	datas = {}
	for col in await db.list_collection_names():
		datas[col] = []
		async for data in db[col].find():
			data.pop("_id", None)
			datas[col].append(data)
	state = await c.invoke(pyrogram.raw.functions.updates.GetState())
	value = {'pts': state.pts, 'qts': state.qts, 'date': state.date}
	data = {'name': 'state', 'value': value}
	datas["bot_settings"].append(data)
	datas = json_util.dumps(datas, indent = 4)
	now = datetime.now()
	now_formatted = now.strftime("%Y%m%d-%H:%M:%S")
	filename = f"backup-mayuri-{now_formatted}.json"
	f = io.BytesIO(datas.encode('utf8'))
	f.name = filename
	await c.send_document(chat_id=chat_id, document=f)
	db2 = AsyncClient(config['bot']['DATABASE_URL'])["mayuri_sessions"]
	datas2 = {}
	for col2 in await db2.list_collection_names():
		datas2[col2] = []
		async for data2 in db2[col2].find():
			datas2[col2].append(data2)
	datas2 = json_util.dumps(datas2, indent = 4)
	filename2 = f"backup-mayuri_sessions-{now_formatted}.json"
	f2 = io.BytesIO(datas2.encode('utf8'))
	f2.name = filename2
	await c.send_document(chat_id=chat_id, document=f2)
	return True
