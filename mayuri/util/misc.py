import httpx
import re
from pyrofork import emoji
from pyrofork.types import InlineKeyboardButton

_EMOJI_REGEXP = None

class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text

async def paginate_plugins(client, _page_n, plugin_dict, prefix, chat_id, chat=None):
    if not chat:
        plugins = sorted(
            [EqInlineKeyboardButton(await client.tl(chat_id, x.__PLUGIN__),
                                    callback_data="{}_plugin({})".format(prefix, x.__PLUGIN__.lower())) for x
             in plugin_dict.values()])
    else:
        plugins = sorted(
            [EqInlineKeyboardButton(await client.tl(chat_id, x.__PLUGIN__),
                                    callback_data="{}_plugin({},{})".format(prefix, chat, x.__PLUGIN__.lower())) for x
             in plugin_dict.values()])

    pairs = [
    plugins[i * 3:(i + 1) * 3] for i in range((len(plugins) + 3 - 1) // 3)
    ]
    round_num = len(plugins) / 3
    calc = len(plugins) - round(round_num)
    if calc == 1:
        pairs.append((plugins[-1], ))
    elif calc == 2:
        pairs.append((plugins[-1],))

    return pairs

def get_emoji_regex():
    global _EMOJI_REGEXP
    if not _EMOJI_REGEXP:
        e_list = [
            getattr(emoji, e).encode("unicode-escape").decode("ASCII")
            for e in dir(emoji)
            if not e.startswith("_")
        ]
        # to avoid re.error excluding char that start with '*'
        e_sort = sorted([x for x in e_list if not x.startswith("*")], reverse=True)
        # Sort emojis by length to make sure multi-character emojis are
        # matched first
        pattern_ = f"({'|'.join(e_sort)})"
        _EMOJI_REGEXP = re.compile(pattern_)
    return _EMOJI_REGEXP


EMOJI_PATTERN = get_emoji_regex()
timeout = httpx.Timeout(40, pool=None)
http = httpx.AsyncClient(http2=True, timeout=timeout)
