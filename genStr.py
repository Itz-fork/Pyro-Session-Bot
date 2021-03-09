import asyncio

from bot import bot, HU_APP
from pyromod import listen
from asyncio.exceptions import TimeoutError

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    SessionPasswordNeeded, FloodWait,
    PhoneNumberInvalid, ApiIdInvalid,
    PhoneCodeInvalid, PhoneCodeExpired
)

API_TEXT = """Hi, {}.
I'm Pyro String Session Bot. I can generate String Session for Your Telegram Account 😉️!

**Hosted and Maintained with ❤️ by @NexaBotsUpdates**

OK now send me Your **`API_ID`** to Start Generating String Session."""
HASH_TEXT = "Ok now send your **`API_HASH`**.\n\nPress /cancel to Cancel Current Task 😋️."
PHONE_NUMBER_TEXT = (
    "Ok now send me your Phone Number in International Format. \n"
    "Including Country code. For a Example: **+94707172659**\n\n"
    "Press /cancel to Cancel Current Task 😋️."
)

@bot.on_message(filters.private & filters.command("start"))
async def genStr(_, msg: Message):
    chat = msg.chat
    api = await bot.ask(
        chat.id, API_TEXT.format(msg.from_user.mention)
    )
    if await is_cancel(msg, api.text):
        return
    try:
        check_api = int(api.text)
    except Exception:
        await msg.reply("Hmm... **`API_ID`** is Invalid 😒️.\nPress /start to Try Again.")
        return
    api_id = api.text
    hash = await bot.ask(chat.id, HASH_TEXT)
    if await is_cancel(msg, hash.text):
        return
    if not len(hash.text) >= 30:
        await msg.reply("Hmm... **`API_HASH`** is Invalid 😒️.\nPress /start to Try Again.")
        return
    api_hash = hash.text
    while True:
        number = await bot.ask(chat.id, PHONE_NUMBER_TEXT)
        if not number.text:
            continue
        if await is_cancel(msg, number.text):
            return
        phone = number.text
        confirm = await bot.ask(chat.id, f'`Is "{phone}" number correct? 🤔️ (Y/N):` \n\nSend: If Yes Send **`y`**\nIf Now Send **`n`**')
        if await is_cancel(msg, confirm.text):
            return
        if "y" in confirm.text:
            break
    try:
        client = Client("my_account", api_id=api_id, api_hash=api_hash)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`\nPress /start to Try Again.")
        return
    try:
        await client.connect()
    except ConnectionError:
        await client.disconnect()
        await client.connect()
    try:
        code = await client.send_code(phone)
        await asyncio.sleep(1)
    except FloodWait as e:
        await msg.reply(f"You have Floodwait of {e.x} Seconds 😃️")
        return
    except ApiIdInvalid:
        await msg.reply("**API ID** and **API Hash** are Invalid 😑️.\n\nPress /start to Try Again.")
        return
    except PhoneNumberInvalid:
        await msg.reply("**Your Phone Number** is Invalid 😑️.\n\nPress /start to Try Again.")
        return
    try:
        otp = await bot.ask(
            chat.id, ("An **OTP** is sent to your phone number, "
                      "Please enter OTP in `1 2 3 4 5` format. __(Space between each numbers!)__ \n\n"
                      "If Bot not sending OTP then try /restart and Start Task again with /start command to Bot.\n"
                      "Press /cancel to Cancel Current Task."), timeout=300)

    except TimeoutError:
        await msg.reply("Hmm.. Time limit reached of 5 min 🙄️.\nPress /start to try Again.")
        return
    if await is_cancel(msg, otp.text):
        return
    otp_code = otp.text
    try:
        await client.sign_in(phone, code.phone_code_hash, phone_code=' '.join(str(otp_code)))
    except PhoneCodeInvalid:
        await msg.reply("Why you entered an **Invalid Code** 😑️.\n\nPress /start to Try Again.")
        return
    except PhoneCodeExpired:
        await msg.reply("Oops..! Code is Expired 😶️.\n\nPress /start to Try Again.")
        return
    except SessionPasswordNeeded:
        try:
            two_step_code = await bot.ask(
                chat.id, 
                "Oh You are a Smart Guy!😁️ Your account have Two-Step Verification.\nNow Please enter your Password.\n\nPress /cancel to Cancel Current Process.",
                timeout=300
            )
        except TimeoutError:
            await msg.reply("`Time limit reached of 5 minutes.\n\nPress /start to Try Again.`")
            return
        if await is_cancel(msg, two_step_code.text):
            return
        new_code = two_step_code.text
        try:
            await client.check_password(new_code)
        except Exception as e:
            await msg.reply(f"**ERROR:** `{str(e)}`")
            return
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return
    try:
        session_string = await client.export_session_string()
        await client.send_message("me", f"#PYRO #STRING_SESSION #NexaBots\n\n```{session_string}``` \n\nBy [@PyroStringSession_bot](https://t.me/PyroStringSession_bot) \nA Powerful Bot by **@NexaBotsUpdates**")
        await client.disconnect()
        text = "Yay! String Session is Successfully Generated 😌️.\nClick on Below Button."
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="🔰️ String Session 🔰️", url=f"tg://openmessage?user_id={chat.id}")]]
        )
        await bot.send_message(chat.id, text, reply_markup=reply_markup)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return


@bot.on_message(filters.private & filters.command("restart"))
async def restart(_, msg: Message):
    await msg.reply("Restarted Bot!")
    HU_APP.restart()


@bot.on_message(filters.private & filters.command("help"))
async def restart(_, msg: Message):
    out = f"""
Hi, {msg.from_user.mention}. I'm **Pyro String Session Bot** \
 I can generate String Session for Your Telegram Account 😉️(UserBot) !

It needs Your **`API_ID`**, **`API_HASH`**, **Phone Number** and **One Time Verification Code**. \
Which will be sent to your Phone Number.
You have to put **OTP** in `1 2 3 4 5` this format. __(Space between each numbers!)__

**NOTE:** If bot not Sending OTP to your Phone Number than send /restart Command and again send /start to Start your Process. 

You must Join [My Updates Channel](https://t.me/NexaBotsUpdates) for Updates! **Hosted and Maintained with ❤️ by @NexaBotsUpdates**
"""
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('⚜️ Support Group ⚜️', url='https://t.me/Nexa_bots'),
                InlineKeyboardButton('❓️ Dev❓️ ', url='https://t.me/TcKnightsForReal')
            ],
            [
                InlineKeyboardButton('🔰️ Bot Channel 🔰️', url='https://t.me/NexaBotsUpdates'),
            ]
        ]
    )
    await msg.reply(out, reply_markup=reply_markup)


async def is_cancel(msg: Message, text: str):
    if text.startswith("/cancel"):
        await msg.reply("Process Is Successfully Cancelled.")
        return True
    return False

if __name__ == "__main__":
    bot.run()
