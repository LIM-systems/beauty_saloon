from re import match
from datetime import datetime as dt

from aiogram import types
from aiogram.dispatcher.filters import Text

import bot.CRUD.client as sqlc
import bot.CRUD.common as sqlcom
from bot import loader as ld
from bot.loader import dp
from bot.utils import keyboards as kb
from bot.utils import utils
from bot.utils.states import ClientData, ClientDataChange
from aiogram.dispatcher import FSMContext

import env


async def message_rec(records):
    '''Составить сообщение используя записи клиентов'''
    message = ''
    for id, date, master_name, service, duration, price, estimation in records:
        message += f'''
Время: <b>{date.strftime('%d-%m-%Y %H:%M')}</b>
Продолжительность: <b>{duration}мин.</b>
Мастер: <b>{master_name}</b>
Услуга: <b>{service}</b>
Цена: <b>{price}руб.</b>
'''
    if estimation:
        message += f'Оценка: <b>{estimation}</b>\n\n'
    else:
        message += '\n'
    return message


async def send_message_records(tg_id, records):
    '''Отправить сообщения о записях клиенту'''
    for id, date, master_name, service, duration, price, estimation in records:
        message = f'''
Время: <b>{date.strftime('%d-%m-%Y %H:%M')}</b>
Продолжительность: <b>{duration}мин.</b>
Мастер: <b>{master_name}</b>
Услуга: <b>{service}</b>
Цена: <b>{price}руб.</b>
'''
        if estimation:
            message += f'Оценка: <b>{estimation}</b>'
        await ld.bot.send_message(
            chat_id=tg_id,
            text=message,
            disable_notification=True,
            reply_markup=kb.inline_btns(ld.cancel_record, f'cancel/{id}'))


@dp.message_handler(Text(ld.main_menu_buttons[2]))
async def get_client_records(msg: types.Message):
    '''Выдать записи клиента если есть'''
    tg_id = msg.from_user.id
    records: dict = await sqlc.check_client_recors(tg_id)
    client: dict = await sqlc.get_user_info(tg_id)
    finish = records.get('finish')
    not_finish = records.get('not_finish')

    # нет никаких записей
    if not not_finish and not finish:
        await msg.answer(
            '<b>Записи не найдены</b>',
            reply_markup=kb.show_user_main_menu(client.get('id')))
    # есть только будущие записи
    elif not_finish and not finish:
        records = await sqlc.select_client_recors(tg_id, finish=False)
        await send_message_records(tg_id, records)
    # есть только завершенные записи
    elif finish and not not_finish:
        records = await sqlc.select_client_recors(tg_id, finish=True)
        message = await message_rec(records)
        await msg.answer(
            f'<b>Ваши завершенные записи</b>\n{message}',
            reply_markup=kb.show_user_main_menu(client.get('id')))
    # есть и завершенные и будущие записи
    else:
        await msg.answer(
            'Выберите какие записи хотите посмотреть',
            reply_markup=kb.inline_btns(ld.client_records, 'crec'))


@dp.callback_query_handler(Text(startswith='crec'))
async def get_client_records2(call: types.CallbackQuery):
    '''Выдать записи клиента предоставленные кнопками'''
    tg_id = call.from_user.id
    # будущие записи
    if ld.client_records[0] in call.data:
        records = await sqlc.select_client_recors(tg_id, finish=False)
        await send_message_records(tg_id, records)
    # завершенные записи
    elif ld.client_records[1] in call.data:
        records = await sqlc.select_client_recors(tg_id, finish=True)
        message = await message_rec(records)
        await call.message.answer(
            f'<b>Ваши завершенные записи</b>\n{message}',
        )


@dp.callback_query_handler(Text(startswith='cancel'))
async def cancel_record(call: types.CallbackQuery):
    '''Отмена записи'''
    record_id = call.data.split('/')[1]
    record = await sqlc.get_client_record(record_id)
    await call.message.answer(
        f'''Вы действительно хотите отменить запись?
Мы оповестим мастера и администратора об отмене

Дата: {record[1].strftime('%d-%m-%Y %H:%M')}
Мастер: {record[2]}
Услуга: {record[3]}
''',
        reply_markup=kb.inline_btns(
            ld.yes_no, f'conf_cancel/{record_id}', row_width=2)
    )


@dp.callback_query_handler(Text(startswith='conf_cancel'))
async def confirm_cancel_record(call: types.CallbackQuery):
    '''Отмена записи'''
    if ld.yes_no[0] in call.data:
        text = 'Запись отменена!'
        record_id = call.data.split('/')[1]
        await sqlcom.update_visit_journal(record_id, {'cancel': True})
        await call.message.edit_text(text)
        # сообщение админам
        adm_text = await utils.alert_admins_msg(record_id, text)
        await ld.bot.send_message(chat_id=env.CHAT_ADMINS, text=adm_text)
        # сообщение мастеру об отмене
        master__tg_id, master_text = await utils.alert_master_msg(record_id, text)
        await ld.bot.send_message(chat_id=master__tg_id, text=master_text)
    else:
        await call.message.delete()


@dp.callback_query_handler(Text(startswith='estimation/'))
async def estimation(call: types.CallbackQuery):
    '''Оценка услуги'''
    # call.data = visit/record_id/estimate_btn
    record_id = call.data.split('/')[1]
    estimate = call.data.split(' ')[-1]
    await sqlcom.update_visit_journal(record_id, {'estimation': estimate})
    if int(estimate) >= 4:
        await call.message.edit_text('Благодарим за оценку! ❤️')
    # оценка 3 и ниже, просим дать комментарий
    else:
        await call.message.edit_text(
            'Пожалуйста оставьте комментарий по оказанной услуге и отправьте сообщением',
            reply_markup=kb.inline_btns(
                (ld.confirm_btn[1],), f'comment/{record_id}'))
        await ClientData.comment.set()


@dp.callback_query_handler(Text(startswith='comment/'))
async def cancel_comment(call: types.CallbackQuery, state: FSMContext):
    '''Отказ от комментария'''
    # call.data = comment/record_id/confirm_btn[1]
    record_id = call.data.split('/')[1]
    await sqlcom.update_visit_journal(
        record_id, {'description': 'Отказ от комметария'})
    await state.finish()
    await call.message.edit_text('Спасибо!')


@dp.message_handler(state=ClientData.comment)
async def set_comment(msg: types.Message, state: FSMContext):
    '''Запись коммента плохой оценки в БД'''
    if '/start' in msg.text or msg.text in ld.main_menu_buttons:
        await msg.answer('Пожалуйста оставьте текстовый комментарий и отправьте сообщением')
        return
    tg_id = msg.from_user.id
    record_id = await sqlc.get_client_record_with_bad_estimate(tg_id)
    if record_id:
        await sqlcom.update_visit_journal(record_id, {'description': msg.text})
    client: dict = await sqlc.get_user_info(tg_id)
    await msg.answer(
        'Благодарим за оценку! ❤️\nМы обязательно прочитаем ваш отзыв!',
        reply_markup=kb.show_user_main_menu(client.get('id')))
    await state.finish()


@dp.message_handler(Text(ld.main_menu_buttons[0]))
async def show_profile(msg: types.Message):
    user_data = await sqlc.get_user_info(msg.from_user.id)
    name = user_data.get('name')
    phone = user_data.get('phone')
    message = f'''Профиль

Имя: <b>{name}</b>
Телефон: <b>{phone}</b>

Что желаете изменить?
'''
    await msg.answer(
        message,
        reply_markup=kb.inline_btns(ld.profile_btn, 'change_profile'))


@dp.callback_query_handler(Text(startswith='change_profile'))
async def get_new_data(call: types.CallbackQuery):
    '''Получить новые данные профиля'''
    await call.message.delete()
    if ld.profile_btn[0] in call.data:
        await ClientDataChange.name.set()
        await call.message.answer('Введите новое Фамилию Имя')
    elif ld.profile_btn[1] in call.data:
        await ClientDataChange.phone.set()
        await call.message.answer('Введите новый номер телефона или нажмите кнопку ниже',
                                  reply_markup=kb.send_phone())


@dp.message_handler(state=ClientDataChange.name)
async def set_new_name(msg: types.Message, state: FSMContext):
    '''Запись нового имени'''
    regex = match(r'\D+ \D+', msg.text)
    if msg.text in ld.main_menu_buttons or not regex:
        await msg.answer('<b>Введите правильно Имя Фамилию</b> и отправьте сообщением')
        return
    if '/start' in msg.text:
        await state.finish()
        await msg.answer('Отмена! Вы всегда можете попробовать позже')
        return
    await sqlc.update_client(msg.from_user.id, {'name': msg.text})
    await state.finish()
    await msg.answer('Фамилия Имя изменены')
    await show_profile(msg)


@dp.message_handler(state=ClientDataChange.phone,
                    content_types=['contact', 'text'])
async def set_new_phone(msg: types.Message, state: FSMContext):
    '''Запись нового телефона'''
    phone = msg.contact.phone_number if msg.contact else msg.text
    clear_phone = utils.clean_phone(phone)
    if not clear_phone:
        await msg.answer('<b>Напишите номер телефона в правильном формате.</b>\nНапример 89001112233')
        return
    client_id = await sqlc.update_client(
        msg.from_user.id, {'phone': clear_phone})
    await state.finish()
    await msg.answer('Телефон изменен',
                     reply_markup=kb.show_user_main_menu(client_id))
    await show_profile(msg)


@dp.callback_query_handler(Text(startswith='confirm'))
async def confirm_record(call: types.CallbackQuery):
    '''Подтверждени или отмена записи после уведомления за 2 или 24 часа'''
    visit_id = call.data.split('/')[1]
    if ld.confirm_btn[0] in call.data:
        await call.message.delete()
        await sqlcom.update_visit_journal(visit_id, {'confirmation': dt.now()})
        await call.message.answer('🙏 Благодарим за подтверждение!')
    if ld.confirm_btn[1] in call.data:
        text = 'Запись отменена!'
        await call.message.delete()
        await sqlcom.update_visit_journal(visit_id, {'cancel': True})
        await call.message.answer(text)
        # сообщение админам
        adm_text = await utils.alert_admins_msg(visit_id, text)
        await ld.bot.send_message(chat_id=env.CHAT_ADMINS, text=adm_text)
        # сообщение мастеру об отмене
        master__tg_id, master_text = await utils.alert_master_msg(visit_id, text)
        await ld.bot.send_message(chat_id=master__tg_id, text=master_text)
