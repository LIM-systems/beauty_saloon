import logging
from logging.handlers import RotatingFileHandler
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

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
)

logger = logging.getLogger(__name__)
rotating_handler = RotatingFileHandler(
    'logs/bot_logs.log',
    maxBytes=5 * 1024 * 1024,
    backupCount=5  # Количество резервных копий логов
)
logger.addHandler(rotating_handler)
logger.addHandler(logging.StreamHandler())


main_menu_buttons = ['◾ Профиль', '🟢 Записаться',
                     '️✔️ Мои записи', '🟠 О нас', '📄 Сертификаты']
reg_button = ('🚪 Регистрация',)
master_menu_buttons = ('🟠 Записи на сегодня',
                       '🟡 Записи на завтра', '📅 Календарь', '📅 Web-Календарь')
client_records = ('Будущие', 'Прошедшие',)
cancel_record = ('❌ Отменить запись',)
yes_no = ('✅ Да', '❌ Нет')
estimation = ('⭐ 1', '⭐ 2', '⭐ 3', '⭐ 4', '⭐ 5')
profile_btn = ('Фамилия Имя', 'Телефон')
confirm_btn = ('✅ Подтверждаю', '❌ Отменить')
