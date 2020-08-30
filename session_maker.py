import os, asyncio, re

try:
	import pyrogram
except ModuleNotFoundError:
	print("You need to install pyrogram first!\nSee: https://github.com/AyraHikari/pyrogram-session-maker")
	exit(1)

try:
	os.remove("bot.session")
except:
	pass

def clear():
	if os.name == "posix":
		a = os.system("clear")
	elif os.name == "nt":
		a = os.system("cls")
	else:
		pass

clear()
print("""
 _  _  _       _                        
| || || |     | |                       
| || || | ____| | ____ ___  ____   ____ 
| ||_|| |/ _  ) |/ ___) _ \|    \ / _  )
| |___| ( (/ /| ( (__| |_| | | | ( (/ / 
 \______|\____)_|\____)___/|_|_|_|\____)                                  
""")
print("You need to register to get app_id and api_hash in here:\nhttps://my.telegram.org/apps")
input("Press any key to continue")

def fill_api():
	clear()
	while True:
		api_id = input("Insert app_id: ")
		if str(api_id).isdigit():
			break
		print("Invaild app_id!\n")

	while True:
		app_hash = input("Insert api_hash: ")
		if app_hash:
			break
		print("Invaild api_hash!\n")
	session_maker(api_id, app_hash)

def session_maker(api_id, app_hash):
	clear()
	if re.search("asyncio", pyrogram.__version__):
		bot_token = input("Insert bot token: ")
		app = pyrogram.Client("bot", api_id=api_id, api_hash=app_hash, bot_token=bot_token)
		ses = "bot.session"
		sestxt = "bot.txt"

		async def start_app():
			await app.start()
			session = app.export_session_string()
			print(f"Done!\nYour session string is:\n\n{session}")
			print(f"\n\nSession string will saved as {sestxt}, Also you can copy {ses} to session dir if need.\nNever share this to anyone!")
			open(sestxt, "w").write(str(session))

		asyncio.get_event_loop().run_until_complete(start_app())

	else:
		bot_token = input("Insert bot token: ")
		app = pyrogram.Client("bot", api_id=api_id, api_hash=app_hash, bot_token=bot_token)
		ses = "bot.session"
		sestxt = "bot.txt"
		with app as generation:
			session = generation.export_session_string()
			print(f"Done!\nYour session string is:\n\n{session}")
			print(f"\n\nSession string will saved as {sestxt}, Also you can copy {ses} to session dir if need.\nNever share this to anyone!")
			open(sestxt, "w").write(str(session))
	print("\n\nDo you want to create again with same API?")
	ask = input("[Y/N] ")
	if ask.lower() == "y":
		session_maker(api_id, app_hash)

fill_api()