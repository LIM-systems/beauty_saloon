from re import sub
from datetime import datetime
from aiogram import types
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from bot.CRUD import client as sqlc


class ClientLastVisitMiddleware(LifetimeControllerMiddleware):
    '''Запись времени посещения бота при любых действиях клиента'''
    skip_patterns = ['error', 'update']

    async def post_process(self, query: types.CallbackQuery, data, *args):
        '''Исполняется после хендлера'''
        # записываем информацию о последнем визите пользователя в базу данных
        await sqlc.update_client(
            tg_id=query.from_user.id,
            params={'last_visit': datetime.now()}
        )


def clean_phone(phone):
    '''Очистка номера от лишних символов
    и приведение номеров к общему синтаксису +7'''
    clear = sub('\D', '', phone)
    if clear.startswith('7') and len(clear) == 11:
        clear = f'+{clear}'
    elif clear.startswith('9') and len(clear) == 10:
        clear = f'+7{clear}'
    elif clear.startswith('8') and len(clear) == 11:
        clear = f'+7{clear[1:]}'
    else:
        return False
    return clear
