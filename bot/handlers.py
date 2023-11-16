from aiogram import types
from aiogram.dispatcher import FSMContext

import bot.django_crud as dj
from bot.loader import dp, bot
from bot.utils import get_telegram_name, show_user_main_menu, saloon_description_main_menu
from bot.states import ClientData


# приветствии при старте бота
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    newbie = await dj.check_for_newbie(msg.from_user.id)
    if newbie:
        message = '''Добро пожаловать!

*Тут информация о салоне*'''
        reg_button = types.InlineKeyboardButton('🚪 Регистрация', callback_data='reg_button')
        keyboard = types.InlineKeyboardMarkup().add(reg_button)
        await msg.answer(message, reply_markup=keyboard)
        return
    message = f'Добро пожаловать в главное меню!\n\n{saloon_description_main_menu}'
    await show_user_main_menu(msg, message)


# кнопка регистрации
@dp.callback_query_handler(lambda call: call.data == 'reg_button')
async def registration(call: types.CallbackQuery):
    await call.message.delete()

    name = await get_telegram_name(call.from_user)

    message = f'''Записать Вас как {name} или желаете указать имя вручную?

P.S. Все указанные данные позже можно будет исправить по желанию.'''
    telegram_name_button = types.InlineKeyboardButton(name, callback_data='telegram_name_button')
    another_name_button = types.InlineKeyboardButton('Написать имя', callback_data='another_name_button')
    keyboard = types.InlineKeyboardMarkup().row(another_name_button, telegram_name_button)
    await call.message.answer(message, reply_markup=keyboard)


# записываем телеграмное имя пользователя и просим номер телефона
@dp.callback_query_handler(lambda call: call.data == 'telegram_name_button')
async def select_telegram_name(call: types.CallbackQuery):
    await call.message.delete()

    name = await get_telegram_name(call.from_user)
    await dj.set_name(call.from_user.id, name)

    await call.message.answer('Отлично! Теперь укажите пожалуйста Ваш номер телефона.')
    await ClientData.phone.set()


# пользователь пожелал указать имя вручную
@dp.callback_query_handler(lambda call: call.data == 'another_name_button')
async def write_own_name(call: types.CallbackQuery):
    await call.message.delete()

    await call.message.answer('Итак, как Вас зовут?')
    await ClientData.name.set()


# запись в бд имени, введённого вручную и просим указать номер телефона
@dp.message_handler(state=ClientData.name)
async def select_own_name(msg: types.Message):
    await dj.set_name(msg.from_user.id, msg.text)
    await msg.answer('Отлично! Теперь укажите пожалуйста Ваш номер телефона.')
    await ClientData.phone.set()


# записываем номер телефона в бд и открываем пользователю главное меню
@dp.message_handler(state=ClientData.phone)
async def set_phone(msg: types.Message, state: FSMContext):
    await dj.set_phone(msg.from_user.id, msg.text)

    message = f'Рады познакомится!\n\n{saloon_description_main_menu}'
    await show_user_main_menu(msg, message)
    await state.finish()