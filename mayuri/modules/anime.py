import asyncio
import html
import imghdr
import json
import math
import os
import pendulum
import requests
import time

from base64 import b64encode
from io import BytesIO, StringIO
from mayuri import Command, AddHandler
from mayuri.modules.disableable import disableable
from Pymoe import Anilist
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import quote as urlencode

@disableable
async def sanime(client, message):
	query = message.text.split(None, 1)
	instance = Anilist()
	r = instance.search.anime(query[1])
	if "data" in r.keys():
		pic = f'{r["data"]["Page"]["media"][0]["coverImage"]["large"]}'
		anime_id = f'{r["data"]["Page"]["media"][0]["id"]}'
		info = f'{r["data"]["Page"]["media"][0]["title"]["romaji"]}\n'
		info += f'{r["data"]["Page"]["media"][0]["title"]["english"]}\n'
		info += f'• Rating: {r["data"]["Page"]["media"][0]["averageScore"]}\n'
		info += f'• Popularity: {r["data"]["Page"]["media"][0]["popularity"]}\n'
		info += f'• Episodes: {r["data"]["Page"]["media"][0]["episodes"]}\n'
		info += f'• Season: {r["data"]["Page"]["media"][0]["season"]}\n'
		info += f'• Adult: {r["data"]["Page"]["media"][0]["isAdult"]}\n'
		url = 'https://anilist.co/anime/'+ anime_id
		button = [[InlineKeyboardButton("Read more", url=url)]]
		if not pic:
			await message.reply_text(info, reply_markup=InlineKeyboardMarkup(button))
		else:
			await message.reply_photo(pic, caption=info, reply_markup=InlineKeyboardMarkup(button))
	else:
		await message.reply_text('cannot reach Anilist API')

def shorten(description, info='anilist.co'):
	ms_g = ""
	if len(description) > 700:
		description = description[0:500] + '....'
		ms_g += f"\n**Description**: __{description}__[Read More]({info})"
	else:
		ms_g += f"\n**Description**: __{description}__"
	return (
		ms_g.replace("<br>", "")
		.replace("</br>", "")
		.replace("<i>", "")
		.replace("</i>", "")
	)


# time formatter from uniborg
def t(milliseconds: int) -> str:
	"""Inputs time in milliseconds, to get beautified time, as string"""
	seconds, milliseconds = divmod(int(milliseconds), 1000)
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
	tmp = ((str(days) + " Days, ") if days else "") + \
		((str(hours) + " Hours, ") if hours else "") + \
		((str(seconds) + " Seconds, ") if seconds else "") + \
		((str(milliseconds) + " ms, ") if milliseconds else "")
	return tmp[:-2]

airing_query = '''
query ($id: Int,$search: String) {
	Media (id: $id, type: ANIME,search: $search) {
		id
		episodes
		title {
			romaji
			english
			native
		}
		nextAiringEpisode {
			airingAt
			timeUntilAiring
			episode
		}
	}
}
'''

fav_query = """
query ($id: Int) { 
	Media (id: $id, type: ANIME) {
		id
		title {
			romaji
			english
			native
		}
	}
}
"""

anime_query = '''
query ($id: Int,$search: String) {
	Media (id: $id, type: ANIME,search: $search) {
		id
		title {
			romaji
			english
			native
		}
		description (asHtml: false)
		startDate{
			year
		}
		episodes
		season
		type
		format
		status
		duration
		siteUrl
		studios{
			nodes{
				name
			}
		}
		trailer{
			id
			site
			thumbnail
		}
		averageScore
		genres
		bannerImage
	}
}
'''

character_query = """
query ($query: String) {
	Character (search: $query) {
		id
		name {
			first
			last
			full
		}
		siteUrl
		image {
			large
		}
		description
	}
}
"""

manga_query = """
query ($id: Int,$search: String) {
	Media (id: $id, type: MANGA,search: $search) {
		id
		title {
			romaji
			english
			native
		}
		description (asHtml: false)
		startDate{
			year
		}
		type
		format
		status
		siteUrl
		averageScore
		genres
		bannerImage
	}
}
"""

url = 'https://graphql.anilist.co'

@disableable
async def airing(client, message):
	search_str = message.text.split(' ', 1)
	if len(search_str) == 1:
		await message.reply_text('Provide anime name!')
		return
	variables = {'search': search_str[1]}
	response = requests.post(
		url, json={'query': airing_query, 'variables': variables}).json()['data']['Media']
	ms_g = f"**Name**: **{response['title']['romaji']}**(`{response['title']['native']}`)\n**ID**: `{response['id']}`"
	if response['nextAiringEpisode']:
		airing_time = response['nextAiringEpisode']['timeUntilAiring'] * 1000
		airing_time_final = t(airing_time)
		ms_g += f"\n**Episode**: `{response['nextAiringEpisode']['episode']}`\n**Airing In**: `{airing_time_final}`"
	else:
		ms_g += f"\n**Episode**:{response['episodes']}\n**Status**: `N/A`"
	await message.reply_text(ms_g)

@disableable
async def anime(client, message):
	search = message.text.split(' ', 1)
	if len(search) == 1:
		await message.delete()
		return
	else:
		search = search[1]
	variables = {'search': search}
	json = requests.post(url, json={'query': anime_query, 'variables': variables}).json()[
		'data'].get('Media', None)
	if json:
		msg = f"**{json['title']['romaji']}**(`{json['title']['native']}`)\n**Type**: {json['format']}\n**Status**: {json['status']}\n**Episodes**: {json.get('episodes', 'N/A')}\n**Duration**: {json.get('duration', 'N/A')} Per Ep.\n**Score**: {json['averageScore']}\n**Genres**: `"
		for x in json['genres']:
			msg += f"{x}, "
		msg = msg[:-2] + '`\n'
		msg += "**Studios**: `"
		for x in json['studios']['nodes']:
			msg += f"{x['name']}, "
		msg = msg[:-2] + '`\n'
		info = json.get('siteUrl')
		trailer = json.get('trailer', None)
		if trailer:
			trailer_id = trailer.get('id', None)
			site = trailer.get('site', None)
			if site == "youtube":
				trailer = 'https://youtu.be/' + trailer_id
		description = json.get(
			'description', 'N/A').replace('<i>', '').replace('</i>', '').replace('<br>', '')
		msg += shorten(description, info)
		image = json.get('bannerImage', None)
		if trailer:
			buttons = [
					[InlineKeyboardButton("More Info", url=info),
					InlineKeyboardButton("Trailer 🎬", url=trailer)]
					]
		else:
		   buttons = [
					[InlineKeyboardButton("More Info", url=info)]
					]
		if image:
			try:
				await message.reply_photo(image, caption=msg, reply_markup=InlineKeyboardMarkup(buttons))
			except:
				msg += f" [〽️]({image})"
				await message.edit(msg)
		else:
			await message.edit(msg)



@disableable
async def character(client, message):
	search = message.text.split(' ', 1)
	if len(search) == 1:
		await message.delete()
		return
	search = search[1]
	variables = {'query': search}
	json = requests.post(url, json={'query': character_query, 'variables': variables}).json()[
		'data'].get('Character', None)
	if json:
		ms_g = f"**{json.get('name').get('full')}**(`{json.get('name').get('native')}`)\n"
		description = f"{json['description']}"
		site_url = json.get('siteUrl')
		ms_g += shorten(description, site_url)
		image = json.get('image', None)
		if image:
			image = image.get('large')
			await message.reply_photo(image, caption=ms_g)
		else:
			await edrep(message, text=ms_g)


@disableable
async def manga(client, message):
	search = message.text.split(' ', 1)
	if len(search) == 1:
		await message.delete()
		return
	search = search[1]
	variables = {'search': search}
	json = requests.post(url, json={'query': manga_query, 'variables': variables}).json()[
		'data'].get('Media', None)
	ms_g = ''
	if json:
		title, title_native = json['title'].get(
			'romaji', False), json['title'].get('native', False)
		start_date, status, score = json['startDate'].get('year', False), json.get(
			'status', False), json.get('averageScore', False)
		if title:
			ms_g += f"**{title}**"
			if title_native:
				ms_g += f"(`{title_native}`)"
		if start_date:
			ms_g += f"\n**Start Date** - `{start_date}`"
		if status:
			ms_g += f"\n**Status** - `{status}`"
		if score:
			ms_g += f"\n**Score** - `{score}`"
		ms_g += '\n**Genres** - '
		for x in json.get('genres', []):
			ms_g += f"{x}, "
		ms_g = ms_g[:-2]

		image = json.get("bannerImage", False)
		ms_g += f"_{json.get('description', None)}_"
		if image:
			try:
				await message.reply_photo(image, caption=ms_g)
			except:
				ms_g += f" [〽️]({image})"
				await edrep(message, text=ms_g)
		else:
			await edrep(message, text=ms_g)

@disableable
async def whatanime(client,message):
	reply = message.reply_to_message
	if reply:
		if reply.photo:
			media = reply.photo
			file_type = "image"
		elif reply.document:
			media = reply.document
			file_type = "document"
		elif reply.video:
			media = reply.video
			file_type = "video"
		else:
			await message.reply_text("Anda harus membalas pesan gambar/gif/video")
			return
		file_id = media.file_id
		if file_type == "image":
			msg = await message.reply_text("Downloading...")
			filename = 'whatanime.png'
			file_path = await client.download_media(file_id)
			image_type = imghdr.what(open('images/whatanime.png', 'rb'))
			if image_type != 'jpeg' and image_type != 'png' and image_type != 'gif':
				await msg.edit("Format file tidak didukung! ({})".format(image_type))
				return
		elif file_type == "document":
			if 'image' in media.mime_type:
				if image_type != 'jpeg' and image_type != 'png' and image_type != 'gif':
					await msg.edit("Format file tidak didukung! ({})".format(image_type))
					return
				filename = 'whatanime.png'
				file_path = await client.download_media(file_id)
			elif 'video' in media.mime_type:
				filename = 'whatanime.mp4'
				file_path = await client.download_media(file_id)
			else:
				await msg.edit("Format file tidak didukung! ({})".format(image_type))
				return
		elif file_type == 'video':
			filename = 'whatanime.mp4'
			file_path = await client.download_media(file_id)
		with open(file_path, 'rb') as f:
			content = b64encode(f.read()).decode("utf-8")
		file = memory_file(filename, content)
		await msg.edit("`Mencari...`")
		url = "https://trace.moe/api/search"
		data = {"image": file}
		raw_resp0 = requests.post(url, data=data).json()
		resp0 = json.dumps(raw_resp0)
		js0 = json.loads(resp0)["docs"]
		if not js0:
			await msg.edit("Hasil tidak ditemukan...")
			return
		js0 = js0[0]
		text = f'<b>{html.escape(js0["title_romaji"])}'
		if js0["title_native"]:
			text += f' ({html.escape(js0["title_native"])})'
		text += "</b>\n"
		if js0["episode"]:
			text += f'<b>Episode:</b> {html.escape(str(js0["episode"]))}\n'
		percent = round(js0["similarity"] * 100, 2)
		text += f"<b>Similarity:</b> {percent}%\n"
		dt0 = pendulum.from_timestamp(js0["from"])
		dt1 = pendulum.from_timestamp(js0["to"])
		text += "<b>At:</b> {}-{}".format(html.escape(dt0.to_time_string()),html.escape(dt1.to_time_string()))
		url = (
			"https://media.trace.moe/video/"
			f'{urlencode(str(js0["anilist_id"]))}'+'/'
			f'{urlencode(js0["filename"])}'
			f'?t={urlencode(str(js0["at"]))}'
			f'&token={urlencode(js0["tokenthumb"])}'
		)
		raw_resp1 = requests.get(url)
		with open("preview.mp4", 'wb') as f:
			f.write(raw_resp1.content)
		file = open("preview.mp4", 'rb')
		await msg.delete()
		try:
			await client.send_chat_action(chat_id=message.chat.id,action="upload_video")
			await message.reply_video(video=file, caption=text)
		except:
			await message.reply_text("`Tidak bisa mengirim preview.`\n{}".format(text))
		os.remove(file_path)
		os.remove("preview.mp4")
	else:
		await message.reply_text("Anda harus membalas pesan gambar/gif/video")

def memory_file(name=None, contents=None, *, bytes=True):
    if isinstance(contents, str) and bytes:
        contents = contents.encode()
    file = BytesIO() if bytes else StringIO()
    if name:
        file.name = name
    if contents:
        file.write(contents)
        file.seek(0)
    return file

AddHandler(sanime,filters.command("sanime", Command))
AddHandler(airing,filters.command("airing", Command))
AddHandler(anime,filters.command("anime", Command))
AddHandler(character,filters.command("character", Command))
AddHandler(manga,filters.command("manga", Command))
AddHandler(whatanime,filters.command("whatanime", Command))
