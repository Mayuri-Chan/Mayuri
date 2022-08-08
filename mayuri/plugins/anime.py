import requests

from mayuri import PREFIX
from mayuri.mayuri import Mayuri
#from mayuri.utils.lang import tl
from Pymoe import Anilist
from pyrogram import filters
from pyrogram.errors import RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Mayuri.on_message(filters.command("sanime", PREFIX))
async def sanime(c, m):
	query = m.text.split(None, 1)
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
			await m.reply_text(info, reply_markup=InlineKeyboardMarkup(button))
		else:
			await m.reply_photo(pic, caption=info, reply_markup=InlineKeyboardMarkup(button))
	else:
		await m.reply_text('cannot reach Anilist API')

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

@Mayuri.on_message(filters.command("airing", PREFIX))
async def airing(c, m):
	search_str = m.text.split(' ', 1)
	if len(search_str) == 1:
		await m.reply_text('Provide anime name!')
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
	await m.reply_text(ms_g)

@Mayuri.on_message(filters.command("anime", PREFIX))
async def anime(c, m):
	search = m.text.split(' ', 1)
	if len(search) == 1:
		await m.delete()
		return
	else:
		search = search[1]
	variables = {'search': search}
	json_data = requests.post(url, json={'query': anime_query, 'variables': variables}).json()[
		'data'].get('Media', None)
	if json_data:
		msg = (f"**{json_data['title']['romaji']}**(`{json_data['title']['native']}`)\n"
		f"**Type**: {json_data['format']}"
		f"\n**Status**: {json_data['status']}\n"
		f"**Episodes**: {json_data.get('episodes', 'N/A')}\n"
		f"**Duration**: {json_data.get('duration', 'N/A')} Per Ep.\n"
		f"**Score**: {json_data['averageScore']}\n**Genres**: `")
		for x in json_data['genres']:
			msg += f"{x}, "
		msg = msg[:-2] + '`\n'
		msg += "**Studios**: `"
		for x in json_data['studios']['nodes']:
			msg += f"{x['name']}, "
		msg = msg[:-2] + '`\n'
		info = json_data.get('siteUrl')
		trailer = json_data.get('trailer', None)
		if trailer:
			trailer_id = trailer.get('id', None)
			site = trailer.get('site', None)
			if site == "youtube":
				trailer = 'https://youtu.be/' + trailer_id
		description = json_data.get(
			'description', 'N/A').replace('<i>', '').replace('</i>', '').replace('<br>', '')
		msg += shorten(description, info)
		image = json_data.get('bannerImage', None)
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
				await m.reply_photo(image, caption=msg, reply_markup=InlineKeyboardMarkup(buttons))
			except RPCError:
				msg += f" [〽️]({image})"
				await m.edit(msg)
		else:
			await m.edit(msg)

@Mayuri.on_message(filters.command("character", PREFIX))
async def character(c, m):
	search = m.text.split(' ', 1)
	if len(search) == 1:
		await m.delete()
		return
	search = search[1]
	variables = {'query': search}
	json_data = requests.post(url, json={'query': character_query, 'variables': variables}).json()[
		'data'].get('Character', None)
	if json_data:
		ms_g = f"**{json_data.get('name').get('full')}**(`{json_data.get('name').get('native')}`)\n"
		description = f"{json_data['description']}"
		site_url = json_data.get('siteUrl')
		ms_g += shorten(description, site_url)
		image = json_data.get('image', None)
		if image:
			image = image.get('large')
			await m.reply_photo(image, caption=ms_g)
		else:
			await m.reply_text(m, text=ms_g)

@Mayuri.on_message(filters.command("manga", PREFIX))
async def manga(c, m):
	search = m.text.split(' ', 1)
	if len(search) == 1:
		await m.delete()
		return
	search = search[1]
	variables = {'search': search}
	json_data = requests.post(url, json={'query': manga_query, 'variables': variables}).json()[
		'data'].get('Media', None)
	ms_g = ''
	if json_data:
		title, title_native = json_data['title'].get(
			'romaji', False), json_data['title'].get('native', False)
		start_date, status, score = json_data['startDate'].get('year', False), json_data.get(
			'status', False), json_data.get('averageScore', False)
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
		for x in json_data.get('genres', []):
			ms_g += f"{x}, "
		ms_g = ms_g[:-2]

		image = json_data.get("bannerImage", False)
		ms_g += f"_{json_data.get('description', None)}_"
		if image:
			try:
				await m.reply_photo(image, caption=ms_g)
			except RPCError:
				ms_g += f" [〽️]({image})"
				await m.reply_text(m, text=ms_g)
		else:
			await m.reply_text(m, text=ms_g)