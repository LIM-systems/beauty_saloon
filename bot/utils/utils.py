from re import sub
from datetime import datetime
from aiogram import types
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from bot.CRUD import client as sqlc
from bot.utils import keyboards as kb


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


async def profile_menu(tg_id, msg):
    user_data = await sqlc.get_user_info(tg_id)
    name = user_data.get('name')
    phone = user_data.get('phone')
    message = f'''Профиль

Имя: <b>{name}</b>
Телефон: <b>{phone}</b>

Что желаете изменить?
'''
    await msg.answer(message, reply_markup=kb.inline_btns(['Имя', 'Телефон'], 'change_profile'))