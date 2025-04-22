import asyncio
import json
import os
from shutil import ExecError
import smtplib
from datetime import datetime as dt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from re import match

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

import bot.CRUD.client as sqlc
import bot.CRUD.common as sqlcom
import env
from bot import loader as ld
from bot.loader import bot, dp
from bot.utils import keyboards as kb
from bot.utils import utils
from bot.utils.states import ClientData, ClientDataChange
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from saloon import settings


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

    if records:
        records = await sqlc.select_client_recors(tg_id, finish=False)
        await send_message_records(tg_id, records)
    else:
        await msg.answer(
            '<b>Записи не найдены</b>',
            reply_markup=kb.show_user_main_menu(client.get('id')))


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
    if int(estimate) == 5:
        await call.message.edit_text('''Благодарим Вас за высокую оценку! Будем признательны, если вы оставите свой отзыв по ссылке:

https://yandex.ru/maps/org/vanil/1174400864/reviews/?ll=37.494512%2C55.681834&tab=reviews&z=15''')
    elif int(estimate) == 4:
        await call.message.edit_text('Благодарим за оценку! ❤️')
    # оценка 3 и ниже, просим дать комментарий
    else:
        await call.message.edit_text(
            'Пожалуйста оставьте комментарий по оказанной услуге и отправьте сообщением',
            reply_markup=kb.inline_btns(
                (ld.confirm_btn[1],), f'comment/{record_id}'))
        await ClientData.comment.set()


@dp.callback_query_handler(Text(startswith='comment/'), state=ClientData.comment)
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


@dp.message_handler(Text(ld.main_menu_buttons[4]))
async def get_certificates_handler(msg: types.Message):
    certificates = await sqlcom.get_certificates()
    sorted_certificates = sorted(certificates, key=lambda c: c.price)

    await kb.get_cert_menu(msg, sorted_certificates)


# показать правила использования сертификатов
@dp.callback_query_handler(lambda c: c.data == 'certificate_button_rules')
async def read_rules(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer('''Правила использования подарочного сертификата салона красоты «Ваниль»

•Подарочные сертификаты  «Ваниль» предоставляют право выбора любой услуги или продукции в салоне.

•Воспользоваться услугой, с использованием подарочного сертификата может как сам Приобретатель сертификата, так и иное лицо, которому Приобретатель подарочного сертификата передал подарочный сертификат. В момент передачи Приобретатель обязуется проинформировать Держателя подарочного сертификата о правилах его использования.

•Срок действия подарочного сертификата 6 месяцев с момента приобретения.В случае если в течение срока действия подарочного сертификата Держатель подарочного сертификата не воспользуется услугой (услугами) салона, то задаток остается в распоряжении Продавца и возврату не подлежит.
 
•Воспользоваться услугами салона по подарочному сертификату можно делать неоднократно до полного расходования его номинала.

•В том случае если Держателем подарочного сертификата выбраны услуги на сумму превышающую номинал карты, Держатель подарочнооо сертификата  имеет право доплатить разницу в стоимости услуги наличными денежными средствами или с помощью банковской карты.

•Подарочный сертификат  возврату и обмену на денежные средства не подлежит.

• Подарочный сертификат необходимо показать администратору до начала оказания услуг.''')


# указать свой номинал сертификата
@dp.callback_query_handler(lambda call: call.data == 'own_cert_sum_button')
async def get_own_sum(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer('Напишите желаемую сумму числами ответным сообщением')
    await ClientData.cert_price.set()


@dp.message_handler(state=ClientData.cert_price)
async def get_own_sum(msg: types.Message, state: FSMContext):
    text = msg.text.replace(' ', '')
    if not text.isdigit() or int(text.replace(' ', '')) < 5000:
        await state.finish()
        await msg.answer('Требуется указать число не менее 5000')
        await asyncio.sleep(1)
        certificates = await sqlcom.get_certificates()
        sorted_certificates = sorted(certificates, key=lambda c: c.price)

        await kb.get_cert_menu(msg, sorted_certificates)
        return

    certificate = await sqlcom.set_certificate(int(text))
    await utils.create_invoice(certificate, bot, msg.from_user.id)
    await state.finish()


# выслать инвойс на покупку сертификата
@dp.callback_query_handler(lambda c: c.data.startswith('certificate_button'))
async def select_certificate(call: types.CallbackQuery):
    id = call.data.split('_')[2]
    certificate = await sqlcom.get_certificate(id)
    await call.message.delete()
    await utils.create_invoice(certificate, bot, call.from_user.id)


# обработка оплаты
@dp.pre_checkout_query_handler()
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# успешный платёж
@dp.message_handler(content_types=types.message.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(msg: types.Message):
    id = msg.successful_payment.invoice_payload
    email = msg.successful_payment.order_info.email
    shopping_entry = await sqlcom.set_shopping_entry(msg.from_user.id, id, email)
    client = shopping_entry.get('client')
    certificate = shopping_entry.get('certificate')
    new_entry = shopping_entry.get('new_entry')
    message = f'''🔔
Покупка сертификата:
Клиент: {client}
Сертификат: {certificate.name}
Цена: {certificate.price}
ID: {shopping_entry.client_cert}
<a href="https://devsaloon.tw1.su/admin/inwork/shoppingjournal/{new_entry.id}/change/">Запись в журнале покупок</a>
'''
    await bot.send_message(chat_id=env.CHAT_ADMINS, text=message)

    client_text = f'''{certificate.name} приобретён!
ID: {shopping_entry.client_cert}'''
    if certificate.image and certificate.image.path:
        with open(certificate.image.path, 'rb') as photo:
            await msg.answer_photo(photo, caption=client_text)
    else:
        await msg.answer(client_text)


@dp.message_handler(commands=['test'])
async def successful_payment(msg: types.Message):
    certificate = await sqlcom.get_certificate(13)
    _, img_buffer = await sqlcom.get_shopping_entry(msg.from_user.id)
    client_text = f'{certificate.name} приобретён!'
    await msg.answer_photo(photo=img_buffer, caption=client_text)

#     message = f'''🔔
# Покупка сертификата:
# Клиент: Василий
# Сертификат: Тестовый
# Цена: 100
# ID: {shopping_entry.client_cert}
# <a href="https://devsaloon.tw1.su/admin/inwork/shoppingjournal/1/change/">Запись в журнале покупок</a>
# '''
#     await bot.send_photo(chat_id=msg.from_user.id, photo=img_buffer, caption=message)
