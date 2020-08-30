import os
import time
import asyncio
from io import BytesIO
from .. import CMD_HELP
from telethon import types
from telethon import events
from datetime import datetime
from telethon.errors import PhotoInvalidDimensionsError
from telethon.tl.functions.messages import SendMediaRequest
from ..utils import admin_cmd, sudo_cmd, progress, edit_or_reply

@borg.on(admin_cmd(pattern="stoi$"))
@borg.on(sudo_cmd(pattern="stoi$",allow_sudo = True))
async def _(cat):
    if cat.fwd_from:
        return
    reply_to_id = cat.message.id
    if cat.reply_to_msg_id:
        reply_to_id = cat.reply_to_msg_id    
    filename = "hi.jpg"
    event = await edit_or_reply(cat ,"Converting.....")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if event.reply_to_msg_id:
        file_name = filename
        reply_message = await event.get_reply_message()
        to_download_directory = Config.TMP_DOWNLOAD_DIRECTORY
        downloaded_file_name = os.path.join(to_download_directory, file_name)
        downloaded_file_name = await borg.download_media( reply_message , downloaded_file_name )
        if os.path.exists(downloaded_file_name):
            caat = await borg.send_file(
                event.chat_id,
                downloaded_file_name,
                force_document=False,
                reply_to = reply_to_id
            )
            os.remove(downloaded_file_name)
            await event.delete()
        else:
            await event.edit("Can't Convert")
    else:
        await event.edit("Syntax : `.stoi` reply to a Telegram normal sticker")

@borg.on(admin_cmd(pattern="itos$"))
@borg.on(sudo_cmd(pattern="itos$",allow_sudo = True))
async def _(cat):
    if cat.fwd_from:
        return
    reply_to_id = cat.message.id
    if cat.reply_to_msg_id:
        reply_to_id = cat.reply_to_msg_id 
    filename = "hi.webp"
    event = await edit_or_reply(cat ,"Converting.....")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if event.reply_to_msg_id:
        file_name = filename
        reply_message = await event.get_reply_message()
        to_download_directory = Config.TMP_DOWNLOAD_DIRECTORY
        downloaded_file_name = os.path.join(to_download_directory, file_name)
        downloaded_file_name = await borg.download_media( reply_message , downloaded_file_name )
        if os.path.exists(downloaded_file_name):
            caat = await borg.send_file(
                event.chat_id,
                downloaded_file_name,
                force_document=False,
                reply_to=reply_to_id
            )   
            os.remove(downloaded_file_name)
            await event.delete()
        else:
            await event.edit("Can't Convert")
    else:
        await event.edit("Syntax : `.itos` reply to a Telegram normal sticker")        

@borg.on(admin_cmd(pattern="ttf ?(.*)"))
@borg.on(sudo_cmd(pattern="ttf ?(.*)",allow_sudo = True))
async def get(event):
    name = event.text[5:]
    if name is None:
        await edit_or_reply(event ,"reply to text message as `.ttf <file name>`")
        return
    m = await event.get_reply_message()
    if m.text:
        with open(name, "w") as f:
            f.write(m.message)
        await event.delete()
        await borg.send_file(event.chat_id,name,force_document=True)
        os.remove(name)
    else:
        await edit_or_reply(event ,"reply to text message as `.ttf <file name>`")
        
@borg.on(admin_cmd(pattern="ftoi$"))
@borg.on(sudo_cmd(pattern="ftoi$",allow_sudo = True))
async def on_file_to_photo(event):
    target = await event.get_reply_message()
    catt = await edit_or_reply(event ,"Converting.....")
    try:
        image = target.media.document
    except AttributeError:
        return
    if not image.mime_type.startswith('image/'):
        return  # This isn't an image
    if image.mime_type == 'image/webp':
        return  # Telegram doesn't let you directly send stickers as photos
    if image.size > 10 * 1024 * 1024:
        return  # We'd get PhotoSaveFileInvalidError otherwise
    file = await borg.download_media(target, file=BytesIO())
    file.seek(0)
    img = await borg.upload_file(file)
    img.name = 'image.png'
    try:
        await borg(SendMediaRequest(
            peer=await event.get_input_chat(),
            media=types.InputMediaUploadedPhoto(img),
            message=target.message,
            entities=target.entities,
            reply_to_msg_id=target.id
        ))
    except PhotoInvalidDimensionsError:
        return
    await catt.delete() 
    
@borg.on(admin_cmd(pattern="nfc ?(.*)"))
@borg.on(sudo_cmd(pattern="nfc ?(.*)",allow_sudo = True))
async def _(event):
    if event.fwd_from:
        return 
    if not event.reply_to_msg_id:
       await edit_or_reply(event ,"```Reply to any media file.```")
       return
    reply_message = await event.get_reply_message() 
    if not reply_message.media:
       await edit_or_reply(event ,"reply to media file")
       return
    input_str = event.pattern_match.group(1)
    if  input_str is None:
        await edit_or_reply(event ,"try `.nfc voice` or`.nfc mp3`")
        return
    if input_str == "mp3":
        event = await edit_or_reply(event ,"converting...")
    elif input_str == "voice":
        event = await edit_or_reply(event ,"converting...")
    else:
        await edit_or_reply(event ,"try `.nfc voice` or`.nfc mp3`")
        return  
    try:
        start = datetime.now()
        c_time = time.time()
        downloaded_file_name = await borg.download_media(
            reply_message,
            Config.TMP_DOWNLOAD_DIRECTORY,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, event, c_time, "trying to download")
            )
        )
    except Exception as e:  # pylint:disable=C0103,W0703
        await event.edit(str(e))
    else:
        end = datetime.now()
        ms = (end - start).seconds
        await event.edit("Downloaded to `{}` in {} seconds.".format(downloaded_file_name, ms))
        new_required_file_name = ""
        new_required_file_caption = ""
        command_to_run = []
        force_document = False
        voice_note = False
        supports_streaming = False
        if input_str == "voice":
            new_required_file_caption = "voice_" + str(round(time.time())) + ".opus"
            new_required_file_name = Config.TMP_DOWNLOAD_DIRECTORY + "/" + new_required_file_caption
            command_to_run = [
                "ffmpeg",
                "-i",
                downloaded_file_name,
                "-map",
                "0:a",
                "-codec:a",
                "libopus",
                "-b:a",
                "100k",
                "-vbr",
                "on",
                new_required_file_name
            ]
            voice_note = True
            supports_streaming = True
        elif input_str == "mp3":
            new_required_file_caption = "mp3_" + str(round(time.time())) + ".mp3"
            new_required_file_name = Config.TMP_DOWNLOAD_DIRECTORY + "/" + new_required_file_caption
            command_to_run = [
                "ffmpeg",
                "-i",
                downloaded_file_name,
                "-vn",
                new_required_file_name
            ]
            voice_note = False
            supports_streaming = True
        else:
            await event.edit("not supported")
            os.remove(downloaded_file_name)
            return
        logger.info(command_to_run)
        # TODO: re-write create_subprocess_exec 😉
        process = await asyncio.create_subprocess_exec(
            *command_to_run,
            # stdout must a pipe to be accessible as process.stdout
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # Wait for the subprocess to finish
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
        os.remove(downloaded_file_name)
        if os.path.exists(new_required_file_name):
            end_two = datetime.now()
            await borg.send_file(
                entity=event.chat_id,
                file=new_required_file_name,
                allow_cache=False,
                silent=True,
                force_document=force_document,
                voice_note=voice_note,
                supports_streaming=supports_streaming,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, event, c_time, "trying to upload")
                )
            )
            ms_two = (end_two - end).seconds
            os.remove(new_required_file_name)
            await event.delete()

CMD_HELP.update({
    "fileconverts":"__**PLUGIN NAME :** File Converts__\
    \n\n📌** CMD ➥** `.stoi` reply to sticker\
    \n**USAGE   ➥  **Converts sticker to image\
    \n\n📌** CMD ➥** `.itos` reply to image\
    \n**USAGE   ➥  **Converts image to sticker\
    \n\n📌** CMD ➥** `.ftoi` reply to image file\
    \n**USAGE   ➥  **Converts Given image file to straemable form\
    \n\n📌** CMD ➥** `.ttf` <file name> reply to text message\
    \n**USAGE   ➥  **Converts Given text message to required file(given file name)\
    \n\n📌** CMD ➥** `.nfc voice` or `.nfc mp3` reply to required media to extract voice/mp3 :\
    \n**USAGE   ➥  **Converts the required media file to voice or mp3 file.\
    "
})    
