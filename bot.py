# By Ryuk

import json
import os
from datetime import datetime

import aiohttp
from dotenv import load_dotenv
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode

if os.path.isfile("config.env"):
    load_dotenv("config.env")

bot = Client(
    name="bot",
    bot_token=os.environ.get("BOT_TOKEN"),
    api_id=int(os.environ.get("API_ID")),
    api_hash=os.environ.get("API_HASH"),
    in_memory=True,
    parse_mode=ParseMode.DEFAULT,
)

CHATS = json.loads(os.environ.get("CHATS"))
BANNER_PATH = os.environ.get("BANNER_PATH")
DEVICE_CHANGELOG = os.environ.get("DEVICE_CHANGELOG")
DEVICE_JSON = os.environ.get("DEVICE_JSON")
RELEASE_CHANNEL = os.environ.get("RELEASE_CHANNEL")
SOURCE_CHANGELOG = os.environ.get("SOURCE_CHANGELOG")
USER = json.loads(os.environ.get("USERS"))

@bot.on_message(filters.command(commands="cpost", prefixes="/") & (filters.chat(CHATS) | filters.user(USER)))
async def make_post(bot, message):
    codename = message.text.replace("/cpost", "").strip()
    if not codename:
        return await message.reply("Give Codename")
    data = await get_json(DEVICE_JSON + codename + ".json")
    if not isinstance(data, dict):
        return await message.reply(data)
    data_dict = data.get("response")[0]
    maintainer = data_dict.get("maintainer")
    data_dict.get("oem")
    device = data_dict.get("device")
    version = data_dict.get("version")
    support_group = data_dict.get("forum")
    telegram_url = data_dict.get("telegram")
    release_date = datetime.now().strftime("%d/%m/%Y")
    notes = await get_notes(codename)
    download_link = notes.get("download") or data_dict.get("download")

    message_ = f"""
#risingOS #TIRAMISU #ROM #{codename}
risingOS v{version} | Official | Android 13
<b>Supported Device:</b> {device} ({codename})
<b>Released:</b> {release_date}
<b>Maintainer:</b> <a href=\"{telegram_url}\">{maintainer}</a>\n
◾<b>Download:</b> <a href=\"{download_link}\">Here</a>
◾<b>Screenshots:</b> <a href=\"https://t.me/riceDroidNews/719\">Here</a>
◾<b>Changelogs:</b> <a href=\"{SOURCE_CHANGELOG}\">Source</a> | <a href=\"{DEVICE_CHANGELOG + codename + ".txt"}\">Device</a>
◾<b>Support group:</b> <a href=\"https://t.me/riceDroidsupport\">Source</a> | <a href=\"{support_group}\">Device</a>\n\n"""

    if note := "\n  ".join(notes.get("notes", [])):
        message_ += f"<b>Notes:</b>\n  {note}\n\n"

    message_ += "<b>Credits:</b>\n  - @not_ayan99 for banner"

    await message.reply_photo(BANNER_PATH + codename + ".png", caption=message_)


async def get_json(url):
    async with (aiohttp.ClientSession() as ses, ses.get(url) as session):
        try:
            response = await session.text()
            response = json.loads(response)
        except Exception:
            response = "Json Not found or is Empty."
    return response


async def get_notes(device):
    raw_url = "https://raw.githubusercontent.com/notayan99/post_bot/main/notes/"
    json_ = await get_json(raw_url + f"{device}.json")
    if not isinstance(json_, dict):
        return {}
    return json_


@bot.on_message(filters.command(commands="post", prefixes="/") & (filters.chat(CHATS) | filters.user(USER)))
async def post_msg(bot, message):
    if not (reply := message.reply_to_message):
        return await message.reply("Reply to a message to post in channel")
    await reply.copy(RELEASE_CHANNEL)
    await message.reply("Posted")


@bot.on_message(filters.command(commands="restart", prefixes="/") & filters.user(USER))
async def restart(bot, message):
    await message.reply("Restarting...")
    print("restarting...")
    os.execl(sys.executable, sys.executable, __file__)


if __name__ == "__main__":
    bot.start()
    print("started")
    idle()
