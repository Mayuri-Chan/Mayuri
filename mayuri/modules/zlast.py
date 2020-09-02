from mayuri import AddHandler
from mayuri.modules.anti_ubot import bl_ubot
from pyrogram import filters

AddHandler(bl_ubot,filters.text & filters.group)