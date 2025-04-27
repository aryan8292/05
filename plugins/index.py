from pyrogram import Client
from pyrogram.errors import MessageNotModified
from pyrogram.types import Message
from database import save_file
import asyncio

async def index_files(bot: Client, msg: Message, chat_id: int, lst_msg_id: int = 0):
    try:
        chat = await bot.get_chat(chat_id)
        title = chat.title
    except Exception as e:
        await msg.edit(f"**Unable to access chat:** `{e}`")
        return

    total = 0
    current = 0
    failed = 0

    try:
        total = await bot.get_messages_count(chat_id)
    except Exception as e:
        await msg.edit(f"**Unable to get total messages:** `{e}`")
        return

    temp = type('obj', (object,), {'CURRENT': 0})()  # creating a temporary object to hold current value

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

            media = None

            if message.video:
                media = message.video
            elif message.document:
                media = message.document
            elif message.audio:
                media = message.audio

            if media:
                try:
                    await save_file(media)
                except Exception as e:
                    failed += 1
                    print(f"Save file error: {e}")
            else:
                failed += 1

            # Edit progress every 100 files (optimized)
            if temp.CURRENT % 100 == 0:
                await update_progress()

        # Final update after completion
        await update_progress()

        await msg.edit(
            f"**Indexing Completed for** `{title}` ✅\n\n"
            f"**Total Messages:** `{total}`\n"
            f"**Processed:** `{temp.CURRENT}`\n"
            f"**Failed:** `{failed}`"
        )

    except Exception as e:
        await msg.edit(f"**Unexpected Error:** `{e}`")

