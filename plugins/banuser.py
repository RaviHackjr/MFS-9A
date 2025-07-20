import asyncio
import os
import random
import sys
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatInviteLink, ChatPrivileges
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import *
from helper_func import *
from database.database import *


@Bot.on_message(filters.private & filters.command('ban') & admin)
async def add_banuser(client: Client, message: Message):        
    pro = await message.reply("<i>Pʀᴏᴄᴇssɪɴɢ ʀᴇǫᴜᴇsᴛ...</i>", quote=True)
    banuser_ids = await db.get_ban_users()
    banusers = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ", callback_data="close")]])

    if not banusers:
        return await pro.edit(
            "<b>Yᴏᴜ ᴍᴜsᴛ ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀ IDs ᴛᴏ ʙᴀɴ.</b>\n\n"
            "<b>Usᴀɢᴇ:</b>\n"
            "<code>/ban [user_id]</code> — Bᴀɴ ᴏɴᴇ ᴏʀ ᴍᴏʀᴇ ᴜsᴇʀs ʙʏ ID.",
            reply_markup=reply_markup
        )

    report, success_count = "", 0
    for uid in banusers:
        try:
            uid_int = int(uid)
        except:
            report += f"Iɴᴠᴀʟɪᴅ ID: <code>{uid}</code>\n"
            continue

        if uid_int in await db.admin_exist(uid) or uid_int == OWNER_ID:
            report += f"Sᴋɪᴘᴘᴇᴅ ᴀᴅᴍɪɴ/ᴏᴡɴᴇʀ ID: <code>{uid_int}</code>\n"
            continue

        if uid_int in banuser_ids:
            report += f"Aʟʀᴇᴀᴅʏ : <code>{uid_int}</code>\n"
            continue

        if len(str(uid_int)) == 10:
            await db.add_ban_user(uid_int)
            report += f"Bᴀɴɴᴇᴅ: <code>{uid_int}</code>\n"
            success_count += 1
        else:
            report += f"⚠Iɴᴠᴀʟɪᴅ Tᴇʟᴇɢʀᴀᴍ ID ʟᴇɴɢᴛʜ﹕ <code>{uid_int}</code>\n"

    if success_count:
        await pro.edit(f"<b>Bᴀɴɴᴇᴅ Usᴇʀs Uᴘᴅᴀᴛᴇᴅ:\n\n{report}</b>", reply_markup=reply_markup)
    else:
        await pro.edit(f"<b>Nᴏ ᴜsᴇʀs ᴡᴇʀᴇ ʙᴀɴɴᴇᴅ.\n\n{report}</b>", reply_markup=reply_markup)

@Bot.on_message(filters.private & filters.command('unban') & admin)
async def delete_banuser(client: Client, message: Message):        
    pro = await message.reply("<i>Pʀᴏᴄᴇssɪɴɢ ʀᴇǫᴜᴇsᴛ...</i>", quote=True)
    banuser_ids = await db.get_ban_users()
    banusers = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ", callback_data="close")]])

    if not banusers:
        return await pro.edit(
            "<b>Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀ IDs ᴛᴏ ᴜɴʙᴀɴ.</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/unban [user_id]</code> — Uɴʙᴀɴ sᴘᴇᴄɪꜰɪᴄ ᴜsᴇʀ(s)\n"
            "<code>/unban all</code> — Rᴇᴍᴏᴠᴇ ᴀʟʟ ʙᴀɴɴᴇᴅ ᴜsᴇʀs",
            reply_markup=reply_markup
        )

    if banusers[0].lower() == "all":
        if not banuser_ids:
            return await pro.edit("<b>Nᴏ ᴜsᴇʀs ɪɴ ᴛʜᴇ ʙᴀɴ ʟɪsᴛ.</b>", reply_markup=reply_markup)
        for uid in banuser_ids:
            await db.del_ban_user(uid)
        listed = "\n".join([f"Uɴʙᴀɴɴᴇᴅ: <code>{uid}</code>" for uid in banuser_ids])
        return await pro.edit(f"<b>Cʟᴇᴀʀᴇᴅ Bᴀɴ Lɪsᴛ:\n\n{listed}</b>", reply_markup=reply_markup)

    report = ""
    for uid in banusers:
        try:
            uid_int = int(uid)
        except:
            report += f"Iɴᴀᴠʟɪᴅ ID: <code>{uid}</code>\n"
            continue

        if uid_int in banuser_ids:
            await db.del_ban_user(uid_int)
            report += f"<b>Uɴʙᴀɴɴᴇᴅ: <code>{uid_int}</b></code>\n"
        else:
            report += f"<b>Nᴏᴛ ɪɴ ʙᴀɴ ʟɪsᴛ: <code>{uid_int}</b></code>\n"

    await pro.edit(f"<b>Uɴʙᴀɴ Rᴇᴘᴏʀᴛ:\n\n{report}</b>", reply_markup=reply_markup)

@Bot.on_message(filters.private & filters.command('banlist') & admin)
async def get_banuser_list(client: Client, message: Message):        
    pro = await message.reply("<i>Fᴇᴛᴄʜɪɴɢ Bᴀɴ Lɪsᴛ...</i>", quote=True)
    banuser_ids = await db.get_ban_users()

    if not banuser_ids:
        return await pro.edit("<b>Nᴏ ᴜsᴇʀs ɪɴ ᴛʜᴇ ʙᴀɴ Lɪsᴛ.</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ", callback_data="close")]]))

    result = "<b>Bᴀɴɴᴇᴅ Usᴇʀs:</b>\n\n"
    for uid in banuser_ids:
        await message.reply_chat_action(ChatAction.TYPING)
        try:
            user = await client.get_users(uid)
            user_link = f'<a href="tg://user?id={uid}">{user.first_name}</a>'
            result += f"• {user_link} — <code>{uid}</code>\n"
        except:
            result += f"• <code>{uid}</code> — <i>Cᴏᴜʟᴅ ɴᴏᴛ ꜰᴇᴛᴄʜ ɴᴀᴍᴇ</i>\n"

    await pro.edit(result, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ", callback_data="close")]]))
