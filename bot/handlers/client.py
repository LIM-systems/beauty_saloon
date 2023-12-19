from aiogram import types
from aiogram.dispatcher.filters import Text

import bot.CRUD.client as sqlc
import bot.CRUD.common as sqlcom
from bot import loader as ld
from bot.loader import dp
from bot.utils import keyboards as kb
from bot.utils import utils
from bot.utils.states import ClientDataChange
from aiogram.dispatcher import FSMContext


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
    finish = records.get('finish')
    not_finish = records.get('not_finish')

    # нет никаких записей
    if not not_finish and not finish:
        await msg.answer('<b>Записи не найдены</b>')
    # есть только будущие записи
    elif not_finish and not finish:
        records = await sqlc.select_client_recors(tg_id, finish=False)
        await send_message_records(tg_id, records)
    # есть только завершенные записи
    elif finish and not not_finish:
        records = await sqlc.select_client_recors(tg_id, finish=True)
        message = await message_rec(records)
        await msg.answer(
            f'<b>Ваши завершенные записи</b>\n{message}')
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
            f'<b>Ваши завершенные записи</b>\n{message}')


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
        record_id = call.data.split('/')[1]
        await sqlcom.update_visit_journal(record_id, {'cancel': True})
        await call.message.edit_text('Запись отменена')
    else:
        await call.message.delete()


@dp.callback_query_handler(Text(startswith='estimation/'))
async def estimation(call: types.CallbackQuery):
    '''Оценка услуги'''
    # call.data = visit/record_id/estimate_btn
    record_id = call.data.split('/')[1]
    estimate = call.data.split(' ')[-1]
    await sqlcom.update_visit_journal(record_id, {'estimation': estimate})
    await call.message.edit_text('Благодарим за оценку! ❤️')


@dp.message_handler(Text(ld.main_menu_buttons[0]))
async def show_profile(msg: types.Message):
    await utils.profile_menu(msg.from_user.id, msg)


@dp.callback_query_handler(Text(startswith='change_profile'))
async def get_new_data(call: types.CallbackQuery):
    '''Получить новые данные профиля'''
    await call.message.delete()
    if 'Имя' in call.data:
        await ClientDataChange.name.set()
        await call.message.answer('Введите новое имя')
    elif 'Телефон' in call.data:
        await ClientDataChange.phone.set()
        await call.message.answer('Введите новый номер телефона', 
                                reply_markup=kb.send_phone())


@dp.message_handler(state=ClientDataChange.name)
async def set_new_name(msg: types.Message, state: FSMContext):
    '''Запись нового имени'''
    await sqlc.update_client(msg.from_user.id, {'name': msg.text})
    await state.finish()
    await msg.answer('Имя изменено')
    await utils.profile_menu(msg.from_user.id, msg)


@dp.message_handler(state=ClientDataChange.phone, content_types=['contact', 'text'])
async def set_new_phone(msg: types.Message, state: FSMContext):
    '''Запись нового телефона'''
    phone = msg.contact.phone_number if msg.contact else msg.text
    clear_phone = utils.clean_phone(phone) or '-'
    await sqlc.update_client(msg.from_user.id, {'phone': clear_phone})
    await state.finish()
    await msg.answer('Телефон изменен',
        reply_markup=kb.show_user_main_menu(msg.from_user.id))
    await utils.profile_menu(msg.from_user.id, msg)