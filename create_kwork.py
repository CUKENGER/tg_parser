import os

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

storage = MemoryStorage()

bot = Bot(token='6981315699:AAEYfmVONOQQNy-tSDHOQO6im33y_1xCpx8')
dp = Dispatcher(bot, storage=MemoryStorage())
