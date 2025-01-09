from aiogram import types

import bot.loader as ld
import env

import logging

logger = logging.getLogger('main')


def menu_keyboard(array: list, row_width=2):
    '''Обычные кнопки для меню
    Принимает список, возвращает кнопки'''
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=row_width)
    markup.add(*array)
    return markup


def send_phone(one_time=True):
    '''Передать телефон'''
    markup = types.ReplyKeyboardMarkup(
        one_time_keyboard=one_time,
        input_field_placeholder='Нажмите на кнопку ниже',
        resize_keyboard=True)
    btn_phone = types.KeyboardButton(
        text='☎️ Передать номер телефона',
        request_contact=True)
    markup.row(btn_phone,)
    return markup


def show_user_main_menu(client_id, row_width=2):
    '''Сообщение с клавиатурой для зерегистрированных по команде /start'''
    print(f'{env.WEB_APP_URL}sign-up?id={client_id}')
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=row_width)
    profile_button = types.KeyboardButton(ld.main_menu_buttons[0])
    sign_up_button = types.KeyboardButton(
        text=ld.main_menu_buttons[1],
        web_app=types.web_app_info.WebAppInfo(
            url=f'{env.WEB_APP_URL}sign-up?id={client_id}'))
    my_entries_button = types.KeyboardButton(
        ld.main_menu_buttons[2])
    about_us_button = types.KeyboardButton(
        ld.main_menu_buttons[3])
    certificates_button = types.KeyboardButton(
        ld.main_menu_buttons[4])
    markup.add(my_entries_button, certificates_button,
               about_us_button, profile_button, sign_up_button)
    return markup


def show_master_main_menu(master_id, row_width=2):
    '''Создание клавиатуры мастера'''
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=row_width)
    today_entries_button = types.KeyboardButton(ld.master_menu_buttons[0])
    tomorrow_entries_button = types.KeyboardButton(
        ld.master_menu_buttons[1])
    calendar_button = types.KeyboardButton(
        ld.master_menu_buttons[2])
    web_calendar_button = types.KeyboardButton(
        text=ld.master_menu_buttons[3],
        web_app=types.web_app_info.WebAppInfo(
            url=f'{env.BASE_URL}visits?id={master_id}'))
    markup.add(today_entries_button, tomorrow_entries_button,
               calendar_button, web_calendar_button)
    return markup


def inline_btns(array: list, call, row_width=1,
                back=False, urls: list = None):
    '''Inline кнопки + URL
    Принимает текст кнопок списком, callback.
    Приинмает ссылки кортеж в списке [(), ()]
    Возвращает кнопки'''
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    for text in array:
        button = types.InlineKeyboardButton(
            text=text,
            callback_data=f'{call}/{text}')
        markup.insert(button)
    if urls:  # добавить URL кнопки, передаем ссылку в кнопки
        for url in urls:
            url_btn = types.InlineKeyboardButton(text=url[0], url=url[1])
            markup.insert(url_btn)
    if back:
        markup.add(types.InlineKeyboardButton(
            '◀◀ Назад', callback_data=f'{call}/◀◀ Назад'))
    return markup


def inline_btns_with_id(array: list, call, row_width=1,):
    '''Inline кнопки
    Принимает текст кнопок списком, callback и ID из БД
    Пример array = [(1, 15), (2, 30), (3, 60)]'''
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    for element in array:
        id, text = element
        button = types.InlineKeyboardButton(
            text=text[:27],
            callback_data=f'{call}/{id}/{text}')
        markup.insert(button)
    markup.add(types.InlineKeyboardButton(
        '◀◀ Назад', callback_data=f'{call}/◀◀ Назад'))
    return markup


def inline_btns_url(array: list, call=None,
                    row_width=1, back=True):
    '''Inline кнопки URL + text'''
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    for element in array:
        text, url = element
        button = types.InlineKeyboardButton(text=text[:40], url=url)
        markup.add(button)
    if back:
        markup.insert(types.InlineKeyboardButton(
            '◀◀ Назад', callback_data=f'{call}/◀◀ Назад'))
    return markup


def inline_btns_with_id_donttext(
        array: list, call, row_width=1,
        back=True, urls=None,
        insert=None,):
    '''Inline кнопки без текста кнопки в callback
    Принимает текст кнопок списком, callback и ID из БД
    Пример array = [(1, 15), (2, 30), (3, 60)]'''
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    if urls:  # добавить URL кнопки, передаем ссылку в кнопки
        for url in urls:
            url_btn = types.InlineKeyboardButton(text=url[0], url=url[1])
            markup.insert(url_btn)
    for element in array:
        id, text = element
        button = types.InlineKeyboardButton(
            text=text,
            callback_data=f'{call}/{id}')
        if insert:
            markup.insert(button)
        else:
            markup.add(button)

    if back:
        if insert:
            markup.insert(types.InlineKeyboardButton(
                '◀◀ Назад', callback_data=f'{call}/◀◀ Назад'))
        else:
            markup.add(types.InlineKeyboardButton(
                '◀◀ Назад', callback_data=f'{call}/◀◀ Назад'))
    return markup
