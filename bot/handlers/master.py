from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

import bot.CRUD.master as sqlm
from bot import loader as ld
from bot.loader import dp
from bot.utils import texts
from bot.utils.states import ClientData
from bot.utils import utils
from bot.utils import keyboards as kb


@dp.message_handler(commands=['master'])
async def start_master(msg: types.Message):
    check_master = await sqlm.check_master(msg.from_user.id)
    if check_master:
        await msg.answer(
            'Вы перешли в меню для мастера!',
            reply_markup=kb.menu_keyboard(ld.master_menu_buttons))
    else:
        await msg.answer(
            'Вы не являетесь мастером нашего салона!',
            reply_markup=kb.menu_keyboard(ld.main_menu_buttons))


async def message_rec(records):
    '''Составить сообщение используя записи клиентов'''
    message = ''
    for id, date, client_name, service, duration, price in records:
        message += f'''
Время: <b>{date.time()}</b>
Клиент: <b>{client_name}</b>
Услуга: <b>{service} :: {duration}мин. :: {price}руб.</b>

'''
    return message


@dp.message_handler(Text(ld.master_menu_buttons[0]))
@dp.message_handler(Text(ld.master_menu_buttons[1]))
async def get_master_work_today(msg: types.Message):
    '''Получить записи мастера на сегодня - завтра'''
    tg_id = msg.from_user.id
    if msg.text == ld.master_menu_buttons[0]:
        date = datetime.now()
    elif msg.text == ld.master_menu_buttons[1]:
        date = datetime.now() + timedelta(days=1)
    records = await sqlm.get_master_work_on_date(tg_id, date.date())

    if not records:
        await msg.answer(f'<b>У Вас нет записей на {date.date()}</b>')
        return
    message = await message_rec(records)
    await msg.answer(
        f'Записи к Вам на <b>{date.strftime("%Y-%m-%d")}</b>\n{message}')


@dp.message_handler(Text(ld.master_menu_buttons[2]))
async def get_master_date_in_records(msg: types.Message):
    '''Выдать даты имеющие запись на услуги'''
    tg_id = msg.from_user.id
    dates = await sqlm.get_dates_master_records(tg_id)
    if not dates:
        await msg.answer(f'<b>Не найдены даты, на которые у Вас есть записи</b>')
        return
    await msg.answer(
        'Даты, на которые у Вас есть записи',
        reply_markup=kb.inline_btns(dates, 'master_date'))


@dp.callback_query_handler(Text(startswith='master_date'))
async def registration(call: types.CallbackQuery):
    '''Ответ на выбор даты'''
    tg_id = call.from_user.id
    date_str = call.data.split('/')[-1]
    date = datetime.strptime(date_str, '%Y-%m-%d')
    records = await sqlm.get_master_work_on_date(tg_id, date)
    message = await message_rec(records)
    await call.message.answer(
        f'Записи к Вам на <b>{date_str}</b>\n{message}')