import asyncio
from async_pymongo import AsyncClient
from bson import json_util

DATABASE_URL = "mongodb://127.0.0.1"

async def restore():
	backup_file = "backup-mayuri.json"
	with open(backup_file) as f:
		datas = json_util.loads(f.read())
	db = AsyncClient(DATABASE_URL)['mayuri']
	for table_name in datas.keys():
		table_data = datas[table_name]
		for data in table_data:
			col = db[table_name]
			await col.insert_one(data)

async def restore_session():
        backup_file = "backup-mayuri_sessions.json"
        with open(backup_file) as f:
                datas = json_util.loads(f.read())
        db = AsyncClient(DATABASE_URL)['mayuri_sessions']
        for table_name in datas.keys():
                table_data = datas[table_name]
                for data in table_data:
                        col = db[table_name]
                        await col.insert_one(data)

asyncio.run(restore())
asyncio.run(restore_session())
