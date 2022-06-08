import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant
from database.database import *
from config import *
from plugins.commands import decode

@Client.on_message(filters.private & filters.incoming)
async def forcesub(c, m):
    owner = await c.get_users(int(OWNER_ID))
    if UPDATE_CHANNEL:
        try:
            user = await c.get_chat_member(UPDATE_CHANNEL, m.from_user.id)
            if user.status == "banned":
               await m.reply_text("**Hey you are banned 😜**", quote=True)
               return
        except UserNotParticipant:
            buttons = [[InlineKeyboardButton(text='Updates Channel 🔖', url=f"https://t.me/{UPDATE_CHANNEL}")]]
            if m.text:
                if (len(m.text.split()) > 1) & ('start' in m.text):
                    decoded_data = await decode(m.text.split()[1])
                    chat_id, msg_id = decoded_data.split('_')
                    buttons.append([InlineKeyboardButton('🔄 Refresh', callback_data=f'refresh+{chat_id}+{msg_id}')])
            await m.reply_text(
                f"Hey {m.from_user.mention(style='md')} you need join My updates channel in order to use me 😉\n\n"
                "__Press the Following Button to join Now 👇__",
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
            return
        except Exception as e:
            print(e)
            await m.reply_text(f"Something Wrong. Please try again later or contact @iDeepBot", quote=True)
            return
    await m.continue_propagation()


@Client.on_callback_query(filters.regex('^refresh'))
async def refresh_cb(c, m):
    owner = await c.get_users(int(OWNER_ID))
    if UPDATE_CHANNEL:
        try:
            user = await c.get_chat_member(UPDATE_CHANNEL, m.from_user.id)
            if user.status == "banned":
               try:
                   await m.message.edit("**Hey you are banned 😜**")
               except:
                   pass
               return
        except UserNotParticipant:
            await m.answer('You are not yet joined our channel. First join and then press refresh button 🤤', show_alert=True)
            return
        except Exception as e:
            print(e)
            await m.message.edit(f"Something Wrong. Please try again later or contact @iDeepBot")
            return

    cmd, chat_id, msg_id = m.data.split("+")
    msg = await c.get_messages(int(chat_id), int(msg_id)) if not DB_CHANNEL_ID else await c.get_messages(int(DB_CHANNEL_ID), int(msg_id))
    if msg.empty:
        return await m.reply_text(f"🥴 **Sorry Sir, your file was deleted!** 🗑\n\n**--Reason--** :\n1. If you stored camrips, adults files, Bot Deleted.\n2. Or Deleted by file Owner.")

    caption = msg.caption.markdown
    as_uploadername = (await get_data(str(chat_id))).up_name
    if as_uploadername:
        if chat_id.startswith('-100'): #if file from channel
            channel = await c.get_chat(int(chat_id))
            caption += "\n\n\n**--Uploader Details :--**\n\n"
            caption += f"**📢 Channel Name :** `{channel.title}`\n"
            caption += f"**🗣 User Name :** @{channel.username}\n" if channel.username else ""
            caption += f"**👤 Channel Id :** `{channel.id}`\n\n"
            caption += f"**💬 DC ID :** {channel.dc_id}\n\n" if channel.dc_id else ""
            caption += f"**👥 Members Count :** {channel.members_count}\n\n" if channel.members_count else ""
        
        else: #if file not from channel
            user = await c.get_users(int(chat_id))
            caption += "\n\n\n**--Uploader Details :--**\n\n"
            caption += f"**🙂 First Name :** `{user.first_name}`\n"
            caption += f"**🙃 Last Name :** `{user.last_name}`\n" if user.last_name else ""
            caption += f"**💥 User Name :** @{user.username}\n" if user.username else ""
            caption += f"**👤 User Id :** `{user.id}`\n\n"
            caption += f"**💬 DC ID :** {user.dc_id}\n\n" if user.dc_id else ""

    await msg.copy(m.from_user.id, caption=caption)
    await m.message.delete()
