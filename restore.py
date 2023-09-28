import asyncio
from async_pymongo import AsyncClient
from bson import json_util

DATABASE_URL = "mongodb://127.0.0.1"
WITH_ENCRYPTION = False
PRIVATE_KEY = "/path/to/private.key"
BACKUP_FILE = "/path/to/mayuri-backup.json"
SESSION_BACKUP_FILE = "/path/to/mayuri_sessions-backup.json"

if WITH_ENCRYPTION:
	from base64 import b64decode
	from nacl.public import PrivateKey, SealedBox
	from nacl.encoding import Base64Encoder

def decrpyt(text) -> str:
	global PRIVATE_KEY
	private_key_file = open(PRIVATE_KEY, 'r').read()
	secret_key = PrivateKey(private_key_file.encode("utf-8"), Base64Encoder())
	unseal_box = SealedBox(secret_key)
	return unseal_box.decrypt(b64decode(text.encode("utf-8")))

async def restore():
	with open(BACKUP_FILE) as f:
		file = f.read()
	if WITH_ENCRYPTION:
		print(f"Decrypting and load data from {BACKUP_FILE}...")
		datas = json_util.loads(decrpyt(file))
	else:
		print(f"Load data from {BACKUP_FILE}...")
		datas = json_util.loads(file)
	print(f"Restoring database...")
	db = AsyncClient(DATABASE_URL)['mayuri']
	for table_name in datas.keys():
		table_data = datas[table_name]
		for data in table_data:
			col = db[table_name]
			await col.insert_one(data)
	print("Done.")

async def restore_session():
	with open(SESSION_BACKUP_FILE) as f:
		file = f.read()
	if WITH_ENCRYPTION:
		print(f"Decrypting and load data from {BACKUP_FILE}...")
		datas = json_util.loads(decrpyt(file))
	else:
		print(f"Load data from {BACKUP_FILE}...")
		datas = json_util.loads(file)
	print(f"Restoring database...")
	db = AsyncClient(DATABASE_URL)['mayuri_sessions']
	for table_name in datas.keys():
		table_data = datas[table_name]
		for data in table_data:
			col = db[table_name]
			await col.insert_one(data)
	print("Done.")

asyncio.run(restore())
asyncio.run(restore_session())
