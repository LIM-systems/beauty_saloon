import logging
import pathlib

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.utils.utils import ClientLastVisitMiddleware

import env

path = pathlib.Path().absolute()
bot = Bot(token=env.TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# регистрация middleware
middleware = ClientLastVisitMiddleware()
dp.middleware.setup(middleware)

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='logs/bot_logs.log',
    level=logging.ERROR,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
)
logger.addHandler(logging.StreamHandler())


main_menu_buttons = ['◾ Профиль', '🟢 Записаться', '️✔️ Мои записи', '🟠 О нас']
reg_button = ('🚪 Регистрация',)
master_menu_buttons = ('🟠 Записи на сегодня',
                       '🟡 Записи на завтра', '📅 Календарь')
client_records = ('Будущие', 'Прошедшие',)
cancel_record = ('❌ Отменить запись',)
yes_no = ('✅ Да', '❌ Нет')
estimation = ('⭐ 1', '⭐ 2', '⭐ 3', '⭐ 4', '⭐ 5')
