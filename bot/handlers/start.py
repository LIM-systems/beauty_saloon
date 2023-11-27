from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

import bot.CRUD.django_crud as dj
from bot import loader as ld
from bot.loader import dp
from bot.utils.utils import get_telegram_name
from bot.utils import texts
from bot.utils.states import ClientData
from bot.utils import keyboards as kb


@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    '''приветствии при старте бота'''
    newbie = await dj.check_for_newbie(msg.from_user.id)
    if newbie:
        await msg.answer(
            '''Добро пожаловать!

*Тут информация о салоне*''',
            reply_markup=kb.inline_btns(ld.reg_button, 'reg_button'))
        return

    await msg.answer(
        f'''Добро пожаловать в главное меню!

{texts.saloon_description_main_menu}''',
        reply_markup=kb.show_user_main_menu(msg.from_user.id))


@dp.callback_query_handler(Text(startswith='reg_button'))
async def registration(call: types.CallbackQuery):
    '''кнопка регистрации'''
    await call.message.delete()

    name = await get_telegram_name(call.from_user)

    message = f'''Записать Вас как {name} или желаете указать имя вручную?

P.S. Все указанные данные позже можно будет исправить по желанию.'''
    telegram_name_button = types.InlineKeyboardButton(
        name, callback_data='telegram_name_button')
    another_name_button = types.InlineKeyboardButton(
        'Написать имя', callback_data='another_name_button')
    keyboard = types.InlineKeyboardMarkup().row(
        another_name_button, telegram_name_button)
    await call.message.answer(message, reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith='telegram_name_button'))
async def select_telegram_name(call: types.CallbackQuery):
    '''записываем телеграмное имя пользователя и просим номер телефона'''
    await call.message.delete()

    name = await get_telegram_name(call.from_user)
    await dj.set_name(call.from_user.id, name)

    await call.message.answer('Отлично! Теперь укажите пожалуйста Ваш номер телефона.')
    await ClientData.phone.set()


@dp.callback_query_handler(Text(startswith='another_name_button'))
async def write_own_name(call: types.CallbackQuery):
    '''пользователь пожелал указать имя вручную'''
    await call.message.delete()

    await call.message.answer('Итак, как Вас зовут?')
    await ClientData.name.set()


@dp.message_handler(state=ClientData.name)
async def select_own_name(msg: types.Message):
    '''запись в бд имени, введённого вручную и просим указать номер телефона'''
    await dj.set_name(msg.from_user.id, msg.text)
    await msg.answer('Отлично! Теперь укажите пожалуйста Ваш номер телефона.')
    await ClientData.phone.set()


@dp.message_handler(state=ClientData.phone)
async def set_phone(msg: types.Message, state: FSMContext):
    '''записываем номер телефона в бд и открываем пользователю главное меню'''
    await dj.set_phone(msg.from_user.id, msg.text)

    await msg.answer(
        f'''Рады познакомится!

{texts.saloon_description_main_menu}''',
        reply_markup=kb.show_user_main_menu(msg.from_user.id))
    await state.finish()
