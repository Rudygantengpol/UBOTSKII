from pyrogram.errors import PeerIdInvalid

from PyroUbot import *

__MODULE__ = "ʙʟᴜꜱᴇʀ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Bluser (Block User Spam)</b></blockquote>

<blockquote><b>perintah : <code>{0}bluser</code> [id/reply]
    Block user yang spam bot.</b></blockquote>

<blockquote><b>perintah : <code>{0}unbluser</code> [id/reply]
    Unblock user yang spam bot.</b></blockquote>

<blockquote><b>perintah : <code>{0}listbluser</code>
    Melihat daftar user yang diblock bot.</b></blockquote>
"""


@PY.BOT("bluser")
@PY.SELLER
async def _(client, message):
    blus = await get_list_from_vars(client.me.id, "BLUSER")
    if len(message.command) > 1:
        user_id = await extract_user(message)
        if not user_id:
            return await message.reply("<b>Balas pesan pengguna atau berikan user_id/username</b>")
        try:
            org = await client.get_users(user_id)
            if org.id in blus:
                return await message.reply("<b>Pengguna sudah didalam blacklist.</b>")
            await add_to_vars(client.me.id, "BLUSER", org.id)
            return await message.reply(
                f"<blockquote><b>✅ Added to blacklist-users.\n"
                f"ID: <code>{org.id}</code>\n"
                f"Name: {org.first_name} {org.last_name or ''}</b></blockquote>"
            )
        except PeerIdInvalid:
            org_id = int(user_id)
            if org_id in blus:
                return await message.reply("<b>Pengguna sudah didalam blacklist.</b>")
            await add_to_vars(client.me.id, "BLUSER", org_id)
            return await message.reply(
                f"<blockquote><b>✅ Added to blacklist-users.\n"
                f"ID: <code>{org_id}</code></b></blockquote>"
            )
    else:
        if not message.reply_to_message or not message.reply_to_message.from_user:
            return await message.reply("<b>Balas pesan pengguna atau berikan user_id/username</b>")
        user_id = message.reply_to_message.from_user.id
        if user_id in blus:
            return await message.reply("<b>Pengguna sudah didalam blacklist.</b>")
        await add_to_vars(client.me.id, "BLUSER", user_id)
        return await message.reply(
            f"<blockquote><b>✅ Added to blacklist-user.\n"
            f"ID: <code>{user_id}</code>\n"
            f"Name: {message.reply_to_message.from_user.first_name}</b></blockquote>"
        )


@PY.BOT("listbluser")
@PY.SELLER
async def _(client, message):
    blus = await get_list_from_vars(client.me.id, "BLUSER")
    if not blus:
        return await message.reply("<b>Belum ada pengguna yang diblacklist!!</b>")
    text = "<blockquote><b>📋 Daftar Blacklist Users:\n\n"
    for count, chat_id in enumerate(blus, 1):
        try:
            user = await client.get_users(int(chat_id))
            text += f"• {count}. <a href=tg://user?id={chat_id}>{user.first_name}</a> | <code>{chat_id}</code>\n"
        except Exception:
            text += f"• {count}. <code>{chat_id}</code>\n"
    text += f"\n⚜️ Total: {len(blus)}</b></blockquote>"
    return await message.reply(text)


@PY.BOT("unbluser")
@PY.SELLER
async def _(client, message):
    blus = await get_list_from_vars(client.me.id, "BLUSER")
    if len(message.command) > 1:
        user_id = await extract_user(message)
        if not user_id:
            return await message.reply("<b>Balas pesan pengguna atau berikan user_id/username</b>")
        try:
            org = await client.get_users(user_id)
            target_id = org.id
        except PeerIdInvalid:
            target_id = int(user_id)

        if target_id not in blus:
            return await message.reply("<b>Pengguna tidak didalam blacklist.</b>")
        await remove_from_vars(client.me.id, "BLUSER", target_id)
        return await message.reply(
            f"<blockquote><b>✅ Removed from blacklist-users.\n"
            f"ID: <code>{target_id}</code></b></blockquote>"
        )
    else:
        if not message.reply_to_message or not message.reply_to_message.from_user:
            return await message.reply("<b>Balas pesan pengguna atau berikan user_id/username</b>")
        user_id = message.reply_to_message.from_user.id
        if user_id not in blus:
            return await message.reply("<b>Pengguna tidak didalam blacklist.</b>")
        await remove_from_vars(client.me.id, "BLUSER", user_id)
        return await message.reply(
            f"<blockquote><b>✅ Removed from blacklist-user.\n"
            f"ID: <code>{user_id}</code></b></blockquote>"
        )
