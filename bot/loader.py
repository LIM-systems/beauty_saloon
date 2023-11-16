import logging
import pathlib

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from saloon.settings import TOKEN

path = pathlib.Path().absolute()
bot = Bot(token=TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)