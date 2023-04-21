# By Ryuk

import json
import os
import sys
from datetime import datetime

import aiohttp
from dotenv import load_dotenv
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from pyrogram.errors import MediaEmpty, WebpageCurlFailed
from telegraph_api import Telegraph
from wget import download

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
TELEGRAPH = Telegraph()
USER = json.loads(os.environ.get("USERS"))


@bot.on_message(filters.command(commands="cpost", prefixes="/") & (filters.chat(CHATS) | filters.user(USER)))
async def make_post(bot, message):
    codename = message.text.replace("/cpost", "").strip()
    if not codename:
        return await message.reply("Give Codename")
    data = await get_json(DEVICE_JSON + codename + ".json")
    if not isinstance(data, dict):
        return await message.reply(data + "\ntip: Query is case sensitive.")
    json_ = data.get("response")[0]
    post = await create_post(json_, codename)
    try:
        await message.reply_photo(BANNER_PATH + codename + ".png", caption=post)
    except (MediaEmpty, WebpageCurlFailed):
        img = download(BANNER_PATH + codename + ".png")
        await message.reply_photo(img, caption=post)
        if os.path.isfile(img):
            os.remove(img)


async def create_post(json_: dict, codename: str):
    message_ = f"""
#risingOS #TIRAMISU #ROM #{codename}
risingOS v{json_.get("version")} | Official | Android 13
<b>Supported Device:</b> {json_.get("device")} ({codename})
<b>Released:</b> {datetime.now().strftime("%d/%m/%Y")}
<b>Maintainer:</b> <a href=\"{json_.get("telegram")}\">{json_.get("maintainer")}</a>\n"""

    notes = await get_notes(codename)
    download_link = notes.get("download") or json_.get("download")

    message_ += f"""
◾<b>Download:</b> <a href=\"{download_link}\">Here</a>
◾<b>Screenshots:</b> <a href=\"https://t.me/riceDroidNews/719\">Here</a>
◾<b>Changelogs:</b> <a href=\"{SOURCE_CHANGELOG}\">Source</a> | <a href=\"{DEVICE_CHANGELOG + codename + ".txt"}\">Device</a>
◾<b>Support group:</b> <a href=\"https://t.me/riceDroidsupport\">Source</a>"""

    if support_group := json_.get("forum"):
        message_ += f'  | <a href="{support_group}">Device</a>'

    credits = "\n\n<b>Credits:</b>\n  - @not_ayan99 for banner"

    if note := "\n  ".join(notes.get("notes", [])):
        if len(note + message_ + credits) > 1024:
            rom_notes = f" **[Here]({await post_to_telegraph('  '+note)})"
        else:
            rom_notes = "\n  " + note
        message_ += f"\n\n<b>Notes:</b>{rom_notes}"

    return message_ + credits


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


async def post_to_telegraph(text):
    telegraph = await TELEGRAPH.create_page("Notes", content_html=f"<p>{text}</p>")
    return telegraph.url


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


async def boot():
    await TELEGRAPH.create_account("Rising OS", author_name="Rising Bot")
    print("started")
    await idle()


if __name__ == "__main__":
    bot.start()
    bot.run(boot())
