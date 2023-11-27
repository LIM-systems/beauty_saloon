import logging
import pathlib

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot import handlers
import env

path = pathlib.Path().absolute()
bot = Bot(token=env.TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


main_menu_buttons = ['📄 Профиль', '🖋 Записаться', '📂 Мои записи', '💬 О нас']
reg_button = ('🚪 Регистрация',)
