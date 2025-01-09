import asyncio
from django.utils.timezone import now, timedelta as td

import aioschedule
from aiogram.utils.exceptions import BotBlocked, UserDeactivated

from bot.CRUD import common as sqlcom
from bot.CRUD import client as sqlc
from bot.CRUD.broadcast import start_broadcast
from bot.loader import bot, logger, estimation, confirm_btn
from bot.utils import keyboards as kb

import env


DELTA2 = 2  # часов
DELTA24 = 24  # часов
DELTA_COMPLETED = 10  # минут


async def send_message_schedule(tg_id, text, keyboard=None):
    '''Отправить сообщение'''
    try:
        if keyboard:
            await bot.send_message(
                tg_id, text, reply_markup=keyboard,
                disable_web_page_preview=True)
        else:
            await bot.send_message(tg_id, text, disable_web_page_preview=True)
    except BotBlocked:
        logger.error(f'{tg_id} - пользователь заблокировал бота')
        await sqlc.update_client(tg_id, {'is_blocked': True})
    except UserDeactivated:
        logger.error(f'{tg_id} - пользователь деактивирован')
        await sqlc.update_client(tg_id, {'is_blocked': True})
    except Exception as e:
        logger.error(
            f'Ошибка при отправке сообщения для {tg_id} - {e}')
    await asyncio.sleep(0.2)


def message_formation(visit, notifi=None, complete=None):
    '''Формирование сообщения для напоминания'''
    id, record_time, master_name, client_name, client_tg_id, service, duration, price, confirmation, phone = visit
    text = f'''
Время: <b>{record_time.strftime('%d-%m-%Y %H:%M')}</b>
Продолжительность: <b>{duration}мин.</b>
Мастер: <b>{master_name}</b>
Услуга: <b>{service}</b>
Цена: <b>{price}руб.</b>
'''
    if notifi:
        message = f'''
Напоминаем о вашей записи в салон красоты!
{text}
Наш адрес: <a href="https://yandex.ru/maps/-/CDFeiKjN">Москва, ул. Удальцова, д.30, 1 этаж</a>
    '''
    elif complete:
        message = f'''
<b>Благодарим за посещение нашего салона красоты!</b>
Пожалуйста оцените качество оказанной услуги
{text}
'''
    return message


async def select_records_for_notifications():
    '''Получить все записи клиентов и вышлем если пора напомнить (за 2 и 24 часа)'''
    visits = await sqlcom.select_open_recors()
    # visit = id, record_time, master_name, client_name, client_tg_id, service, duration, price, confirmation
    for visit in visits:
        # если дата-время входит в промежуток данной минуты
        now_delta2 = now() + td(hours=DELTA2)
        now_delta24 = now() + td(hours=DELTA24)
        # время для уведомления админов если не подтверждена
        admin_alert = visit[1] - td(minutes=90)
        # время после оказания услуги (время записи + продолжительность + запас)
        service_completed = visit[1] + td(minutes=visit[6] + DELTA_COMPLETED)
        message_notifi = message_formation(notifi=True, visit=visit)
        # уведомление за 2 часа
        if now_delta2 - td(seconds=30) < visit[1] < now_delta2 + td(seconds=30):
            print('now_delta2', now_delta2, visit[1])
            # отправляем уведомление клиенту
            await send_message_schedule(
                tg_id=visit[4], text=message_notifi,
                keyboard=kb.inline_btns(confirm_btn, f'confirm/{visit[0]}'))
        # уведомление за 24 часа
        if now_delta24 - td(seconds=30) < visit[1] < now_delta24 + td(seconds=30):
            print('now_delta24', now_delta24, visit[1])
            await send_message_schedule(
                tg_id=visit[4], text=message_notifi,
                keyboard=kb.inline_btns(confirm_btn, f'confirm/{visit[0]}'))
        # уведомление об оценке сервиса после оказания услуги
        if now() - td(seconds=30) < service_completed < now() + td(seconds=30):
            print('service_completed', service_completed)
            # отметим запись как завершенную
            await sqlcom.update_visit_journal(
                record_id=visit[0],
                params={'cancel': False, 'finish': True})
            await send_message_schedule(
                tg_id=visit[4],
                text=message_formation(complete=True, visit=visit),
                keyboard=kb.inline_btns(
                    estimation, f'estimation/{visit[0]}', row_width=5)
            )
        # уведомление админов в чат если за 1.5 часа не получено подтверждение от клиента
        if now() - td(seconds=30) < admin_alert < now() + td(seconds=30) and not visit[8]:
            await bot.send_message(
                chat_id=env.CHAT_ADMINS,
                text=f'''
<a href="{env.BASE_URL}admin/inwork/visitjournal/{visit[0]}">
Запись не подтверждена </a>
Клиент: <b>{visit[3]}</b> <code>{visit[9]}</code>
Мастер: <b>{visit[2]}</b>
Услуга: <b>{visit[5]}</b>
Время: <b>{visit[1]}</b>
''')


async def scheduler():
    '''Задания планировщика'''
    aioschedule.every(1).minutes.do(select_records_for_notifications)
    aioschedule.every(1).minutes.do(start_broadcast)  # ручные рассылки
    # aioschedule.every(10).seconds.do(select_records_for_notifications)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())
