import asyncio
import os
import random
import sys
import time
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction, ChatMemberStatus, ChatType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatMemberUpdated, ChatPermissions
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, InviteHashEmpty, ChatAdminRequired, PeerIdInvalid, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import *
from helper_func import *
from database.database import *


@Bot.on_message(filters.command('add_admin') & filters.private & filters.user(OWNER_ID))
async def add_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    check = 0
    admin_ids = await db.get_all_admins()
    admins = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    if not admins:
        return await pro.edit(
            "<b>Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀ ID(s) ᴛᴏ ᴀᴅᴅ ᴀs ᴀᴅᴍɪɴ.</b>\n\n"
            "<b>Usᴀɢᴇ﹕</b>\n"
            "<code>/add_admin [user_id]</code> — Aᴅᴅ ᴏɴᴇ ᴏʀ ᴍᴏʀᴇ ᴜsᴇʀ IDs\n\n"
            "<b>Exᴀᴍᴘʟᴇ﹕</b>\n"
            "<code>/add_admin 1234567890 9876543210</code>",
            reply_markup=reply_markup
        )

    admin_list = ""
    for id in admins:
        try:
            id = int(id)
        except:
            admin_list += f"<blockquote><b>Iɴᴠᴀʟɪᴅ ID: <code>{id}</code></b></blockquote>\n"
            continue

        if id in admin_ids:
            admin_list += f"<blockquote><b>ID <code>{id}</code> ᴀʟʀᴇᴀᴅʏ ᴇxɪsᴛs.</b></blockquote>\n"
            continue

        id = str(id)
        if id.isdigit() and len(id) == 10:
            admin_list += f"<b><blockquote>(ID: <code>{id}</code>) ᴀᴅᴅᴇᴅ.</blockquote></b>\n"
            check += 1
        else:
            admin_list += f"<blockquote><b>Iɴᴠᴀʟɪᴅ ID: <code>{id}</code></b></blockquote>\n"

    if check == len(admins):
        for id in admins:
            await db.add_admin(int(id))
        await pro.edit(f"<b>Aᴅᴍɪɴ(s) ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ﹕</b>\n\n{admin_list}", reply_markup=reply_markup)
    else:
        await pro.edit(
            f"<b>Sᴏᴍᴇ ᴇʀʀᴏʀs ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴀᴅᴅɪɴɢ ᴀᴅᴍɪɴs﹕</b>\n\n{admin_list.strip()}\n\n"
            "<b><i>Pʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</i></b>",
            reply_markup=reply_markup
        )


@Bot.on_message(filters.command('deladmin') & filters.private & filters.user(OWNER_ID))
async def delete_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    admin_ids = await db.get_all_admins()
    admins = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    if not admins:
        return await pro.edit(
            "<b>Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴠᴀʟɪᴅ ᴀᴅᴍɪɴ ID⁽s⁾ ᴛᴏ ʀᴇᴍᴏᴠᴇ.</b>\n\n"
            "<b>Usᴀɢᴇ﹕</b>\n"
            "<code>/deladmin [user_id]</code> — Rᴇᴍᴏᴠᴇ sᴘᴇᴄɪꜰɪᴄ IDs\n"
            "<code>/deladmin all</code> — Rᴇᴍᴏᴠᴇ ᴀʟʟ ᴀᴅᴍɪɴs",
            reply_markup=reply_markup
        )

    if len(admins) == 1 and admins[0].lower() == "all":
        if admin_ids:
            for id in admin_ids:
                await db.del_admin(id)
            ids = "\n".join(f"<blockquote><code>{admin}</code></blockquote>" for admin in admin_ids)
            return await pro.edit(f"<b>Aʟʟ ᴀᴅᴍɪɴ IDs ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ﹕</b>\n{ids}", reply_markup=reply_markup)
        else:
            return await pro.edit("<b><blockquote>Nᴏ ᴀᴅᴍɪɴ IDs ᴛᴏ ʀᴇᴍᴏᴠᴇ.</blockquote></b>", reply_markup=reply_markup)

    if admin_ids:
        passed = ''
        for admin_id in admins:
            try:
                id = int(admin_id)
            except:
                passed += f"<blockquote><b>Iɴᴠᴀʟɪᴅ ID: <code>{admin_id}</code></b></blockquote>\n"
                continue

            if id in admin_ids:
                await db.del_admin(id)
                passed += f"<blockquote><code>{id}</code> Rᴇᴍᴏᴠᴇᴅ</blockquote>\n"
            else:
                passed += f"<blockquote><b>ID <code>{id}</code> ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ᴀᴅᴍɪɴ ʟɪsᴛ.</b></blockquote>\n"

        await pro.edit(f"<b>Aᴅᴍɪɴ ʀᴇᴍᴏᴠᴀʟ ʀᴇsᴜʟᴛ﹕\n\n{passed}</b>", reply_markup=reply_markup)
    else:
        await pro.edit("<b><blockquote>Nᴏ ᴀᴅᴍɪɴ IDs ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ.</blockquote></b>", reply_markup=reply_markup)


@Bot.on_message(filters.command('admins') & filters.private & admin)
async def get_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    admin_ids = await db.get_all_admins()

    if not admin_ids:
        admin_list = "<b><blockquote>Nᴏ ᴀᴅᴍɪɴs ꜰᴏᴜɴᴅ.</blockquote></b>"
    else:
        admin_list = "\n".join(f"<b><blockquote>ID: <code>{id}</code></blockquote></b>" for id in admin_ids)

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])
    await pro.edit(f"<b>⚡ Cᴜʀʀᴇɴᴛ Aᴅᴍɪɴ Lɪsᴛ﹕\n\n{admin_list}</b>", reply_markup=reply_markup)
