from aiogram import types
from aiogram.types.web_app_info import WebAppInfo
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

API_URL = os.environ.get('API_URL')
BASE_URL = os.environ.get('BASE_URL')

# получение имени из телеграма
async def get_telegram_name(user):
    if not user.first_name:
        name = user.last_name
    elif not user.last_name:
        name = user.first_name
    else:
        name = user.first_name + " " + user.last_name
    return name


# информация, выдаваемая зарегистрированным пользователям по команде /start
saloon_description_main_menu = '*Тут какое-либо описание(салона и/или кнопок главного меню)*'

main_menu_buttons = ['📄 Профиль', '🖋 Записаться', '📂 Мои записи', '💬 О нас']

# сообщение с клавиатурой для зерегистрированных по команде /start
async def show_user_main_menu(msg, message):
    telegram_id = msg.from_user.id
    profile_button = types.KeyboardButton(main_menu_buttons[0])
    sign_up_button = types.KeyboardButton(text=main_menu_buttons[1],
    web_app=WebAppInfo(url=BASE_URL + f'sign_in/{telegram_id}/'))
    my_entries_button = types.KeyboardButton(main_menu_buttons[2])
    about_us_button = types.KeyboardButton(main_menu_buttons[3])
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)\
    .row(my_entries_button, sign_up_button)\
    .row(about_us_button, profile_button)
    await msg.answer(message, reply_markup=keyboard)


async def main_menu_buttons_handle(msg: types.Message, button: str) -> None:
    if main_menu_buttons[0]:
        await msg.answer('Команда в разработке')
    if main_menu_buttons[2]:
        await msg.answer('Команда в разработке')
    if main_menu_buttons[3]:
        await msg.answer('Команда в разработке')