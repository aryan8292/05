from pyrogram import Client
from pyrogram.errors import MessageNotModified
from pyrogram.types import Message
from database.ia_filterdb import save_file  # ✅ fixed import
import asyncio

async def index_files(bot: Client, msg: Message, chat_id: int, lst_msg_id: int = 0):
    try:
        chat = await bot.get_chat(chat_id)
        title = chat.title
    except Exception as e:
        await msg.edit(f"**Unable to access chat:** `{e}`")
        return

    total = 0
    failed = 0

    try:
        total = await bot.get_messages_count(chat_id)
    except Exception as e:
        await msg.edit(f"**Unable to get total messages:** `{e}`")
        return

    temp = type('obj', (object,), {'CURRENT': 0})()

    async def update_progress():
        try:
            await msg.edit(
                f"**Indexing `{title}`**\n\n"
                f"**Total Messages:** `{total}`\n"
                f"**Processed:** `{temp.CURRENT}`\n"
                f"**Failed:** `{failed}`"
            )
        except MessageNotModified:
            pass
        except Exception as e:
            print(f"Edit error: {e}")

    await msg.edit(f"**Starting Indexing for** `{title}`...\n\nPlease wait.")

    try:
        async for message in bot.iter_messages(chat_id, offset_id=lst_msg_id):
            temp.CURRENT += 1

            if not message:
                failed += 1
                continue

            media = message.video or message.document or message.audio

            if media:
                try:
                    await save_file(media)
                except Exception as e:
                    failed += 1
                    print(f"Save file error: {e}")
            else:
                failed += 1

            if temp.CURRENT % 100 == 0:
                await update_progress()

        await update_progress()

        await msg.edit(
            f"**Indexing Completed for** `{title}` ✅\n\n"
            f"**Total Messages:** `{total}`\n"
            f"**Processed:** `{temp.CURRENT}`\n"
            f"**Failed:** `{failed}`"
        )

    except Exception as e:
        await msg.edit(f"**Unexpected Error:** `{e}`")
