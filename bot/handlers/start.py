from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

import bot.CRUD.django_crud as dj
from bot import loader as ld
from bot.loader import dp
from bot.utils import texts
from bot.utils.states import ClientData
from bot.utils import utils
from bot.utils import keyboards as kb


@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    '''приветствии при старте бота'''
    newbie = await dj.check_for_newbie(
        msg.from_user.id,
        msg.from_user.full_name)
    if newbie:
        await msg.answer(
            texts.welcome,
            reply_markup=kb.inline_btns(ld.reg_button, 'reg_btn'))
        return

    await msg.answer(
        texts.about_bot,
        reply_markup=kb.show_user_main_menu(msg.from_user.id))


@dp.callback_query_handler(Text(startswith='reg_btn'))
async def registration(call: types.CallbackQuery):
    '''кнопка регистрации'''
    await call.message.delete()
    name = call.message.chat.full_name
    message = f'''Записать Вас как <b>{name}</b> или желаете указать имя вручную?

P.S. Все указанные данные позже можно будет исправить по желанию.'''
    telegram_name_button = types.InlineKeyboardButton(
        name, callback_data='get_name_tg')
    another_name_button = types.InlineKeyboardButton(
        'Написать имя', callback_data='get_name_another')
    keyboard = types.InlineKeyboardMarkup().row(
        another_name_button, telegram_name_button)
    await call.message.answer(message, reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith='get_name'))
async def select_telegram_name(call: types.CallbackQuery):
    '''записываем телеграмное имя пользователя и просим номер телефона
    или просим ввести имя'''
    name = call.message.chat.full_name
    # записываем телеграмное имя пользователя и просим номер телефона
    if 'get_name_tg' in call.data:
        await dj.update_client(call.from_user.id, {'name': name})
        await call.message.answer(
            texts.get_phone_text, reply_markup=kb.send_phone())
        await ClientData.phone.set()
    elif 'get_name_another' in call.data:
        await call.message.edit_text('Отправьте своё имя сообщением')
        await ClientData.name.set()


@dp.message_handler(state=ClientData.name)
async def select_own_name(msg: types.Message):
    '''запись в бд имени, введённого вручную и просим указать номер телефона'''
    await dj.update_client(msg.from_user.id, {'name': msg.text})
    await msg.answer(texts.get_phone_text, reply_markup=kb.send_phone())
    await ClientData.phone.set()


@dp.message_handler(state=ClientData.phone, content_types=['contact'])
@dp.message_handler(state=ClientData.phone)
async def set_phone(msg: types.Message, state: FSMContext):
    '''записываем номер телефона в бд и открываем пользователю главное меню'''
    phone = msg.contact.phone_number if msg.contact else msg.text
    clear_phone = utils.clean_phone(phone)
    if msg.text == '/start':
        await msg.answer('Для регистрации отправьте свой номер телефона или контакт')
        return
    if not clear_phone:
        await msg.answer('Напишите номер телефона в правильном формате. Например 89001112233')
        return
    await dj.update_client(msg.from_user.id, {'phone': clear_phone})
    await msg.answer(
        texts.about_bot,
        reply_markup=kb.show_user_main_menu(msg.from_user.id))
    await state.finish()
