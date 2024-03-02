import speech_recognition as sr
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from create_kwork import bot
from database.sqlite_db import Database
import config as cfg
from parsing.start_pars import start_pars


db = Database(cfg.path_to_db)




async def recognise(filename):
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio_text = r.listen(source)
        try:
            text = r.recognize_google(audio_text, language='ru_RU')
            return text
        except:
            return False



async def voice_handler(tgid, text):
    commands = {'start_parsing':
                    ['начни анализ', 'начать анализ'],

                'stop_parsing':
                    ['останови анализ', 'стоп анализ']
                }

    if text in commands['start_parsing']:
        await bot.send_message(tgid, '<b>Начинаю парсинг</b>', parse_mode='HTML')
        await db.update_status_user(tgid, 'active')

        scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
        scheduler.add_job(func=start_pars, args=(tgid,), trigger='interval', minutes=5)
        scheduler.start()

    elif text in commands['stop_parsing']:
        await db.update_status_user(tgid, 'inactive')
        await bot.send_message(tgid, '<b>Парсинг остановлен</b>', parse_mode='HTML')

    else:
        await bot.send_message(tgid, 'Не распознал, повтори')
