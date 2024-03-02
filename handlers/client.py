import subprocess
import os

from aiogram import Dispatcher, types
from pathlib import Path
from aiogram.types import ContentType
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from create_kwork import bot
import config as cfg
from database.sqlite_db import Database
from parsing.start_pars import start_pars
from voice.recognize import recognise, voice_handler


db = Database(cfg.path_to_db)


async def start(message: types.Message):
    await message.answer('<b>Привет!</b>\n'
                         'Используй эти команды:\n'
                         '1. <i>/start_pars</i>\n'
                         '2. <i>/stop</i>\n',
                         parse_mode='HTML')
    await message.answer('<b>Голосовое управление</b>\n'
                         '"Начать анализ" - скажите в голосовые сообщения\n'
                         '"Стоп анализ" - скажите в голосовые сообщения',
                         parse_mode='HTML')

    if db.get_status_user(message.from_user.id) is None:
        await db.set_status_user(message.from_user.id, 'inactive')


async def start_parsing(message: types.Message):
    await db.update_status_user(message.from_user.id, 'active')

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(func=start_pars, args=(message.from_user.id,), trigger='interval', seconds=5)
    scheduler.start()

    await message.answer('Парсинг начался')


async def stop_parsing(message: types.Message):
    await db.update_status_user(message.from_user.id, 'inactive')
    await message.answer('<b>Парсинг остановлен</b>', parse_mode='HTML')





async def voice_message_handler(message: types.Message):
    filename_start = f'{message.from_user.id}.ogg'
    filename_finish = f'{message.from_user.id}.wav'

    file_name_full = str(Path(str(Path.cwd()), 'voices', filename_start))
    file_name_full_converted = str(Path(str(Path.cwd()), 'voices', filename_finish))

    file_info = await bot.get_file(message.voice.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    with open(file_name_full, 'wb') as new_file:
        new_file.write(downloaded_file.getvalue())

    subprocess.run("ffmpeg -i " + file_name_full + "  " + file_name_full_converted)

    text = await recognise(file_name_full_converted)

    if text:
        await voice_handler(message.from_user.id, text.lower())
    else:
        await message.answer('Не расслышал, повтори ещё раз')

    os.remove(file_name_full)
    os.remove(file_name_full_converted)




# REGISTRATION
def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'], chat_type='private')
    dp.register_message_handler(start_parsing, commands=['start_pars'], chat_type='private')
    dp.register_message_handler(stop_parsing, commands=['stop'], chat_type='private')
    dp.register_message_handler(voice_message_handler, content_types=[ContentType.VOICE])
