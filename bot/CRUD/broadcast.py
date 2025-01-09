import asyncio
import csv
from datetime import datetime
from os.path import join

from aiogram.utils.exceptions import BotBlocked
from asgiref.sync import sync_to_async
from django.utils.timezone import now, timedelta

from bot.CRUD.client import update_client
from bot.loader import bot
from saloon.settings import MEDIA_ROOT
from inwork.models import Broadcast


@sync_to_async()
def get_all_broadcasts():
    '''Получение заданий на ручную рассылку'''
    # выбрать расылки с временем >= текущего
    broadcasts = Broadcast.objects.filter(
        send_datetime__gte=now() - timedelta(minutes=2)
    )

    return [(item.id, item.send_datetime) for item in broadcasts]


async def select_broadcast():
    '''Проверка на совпадение времени для выбора рассылки на отправку'''
    # список тех кто поставил уведомление с учетом дня недели
    broadcasts = await get_all_broadcasts()
    time_now = now()
    tdelta_plus = time_now + timedelta(seconds=30)
    tdelta_minus = time_now - timedelta(seconds=30)

    if broadcasts:
        time_now = now()  # время сейчас
        for id, send_datetime in broadcasts:
            # + и - 30 cек от текущего времени
            tdelta_plus = time_now + timedelta(seconds=30)
            tdelta_minus = time_now - timedelta(seconds=30)
            # если время входит в промежуток данной минуты добавим в список
            if tdelta_minus < send_datetime < tdelta_plus:
                return id  # вернем id Broadcast для рассылки
    return False


async def start_broadcast():
    '''Получение клиентов для рассылки из csv
    + сама рассылка и запись результата в csv'''
    broadcast_id = await select_broadcast()
    if not broadcast_id:  # если нет рассылок для отправки
        return False

    broadcast: Broadcast = await Broadcast.objects.aget(id=broadcast_id)

    path_start = join(MEDIA_ROOT, 'broadcasts/start')
    # путь к файлу csv
    file_path_start = f'{path_start}/{broadcast.filename}.csv'

    text = broadcast.text
    with open(file_path_start) as csvfile:
        clients = csv.reader(csvfile)
        for full_name, tg_id in clients:
            # рассылка клиентам с заменой тега {name} на Имя Фамилию
            try:
                if broadcast.photo:
                    await bot.send_photo(
                        tg_id, broadcast.photo,
                        caption=text.replace('{name}', full_name))
                elif broadcast.video:
                    await bot.send_video(
                        tg_id, broadcast.video,
                        caption=text.replace('{name}', full_name))
                else:
                    await bot.send_message(
                        tg_id, text.replace('{name}', full_name),
                        disable_web_page_preview=True)

                await add_csv_result_broadcast(
                    broadcast.filename, [full_name, tg_id, 'Доставлено'])
                await asyncio.sleep(0.2)

            except BotBlocked:
                await add_csv_result_broadcast(
                    broadcast.filename, [full_name, tg_id, 'Бот заблокирован'])
                # обновим поле о блокировке бота у пользователя
                await update_client(tg_id, params={'is_blocked': True})
            except Exception as e:

                await add_csv_result_broadcast(
                    broadcast.filename, [full_name, tg_id, f'Ошибка: {e}'])


async def add_csv_result_broadcast(filename, row: list):
    '''Записать результат рассылки '''
    path_finish = join(MEDIA_ROOT, 'broadcasts/finish')
    # путь к файлу csv
    file_path_finish = f'{path_finish}/{filename}.csv'

    with open(file_path_finish, 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(row + [datetime.now().strftime('%Y-%m-%d %H:%M:%S')])


async def start_test_broadcast(broadcast, admins):
    '''Получение клиентов для рассылки из csv
    + сама рассылка и запись результата в csv'''
    if not broadcast:  # если нет рассылок для отправки
        return False

    text = broadcast.text

    for tg_id, name in admins:
        # добавим возможность вставить имя тегом
        if '{name}' in broadcast.text:
            text = text.replace('{name}', name)
        if broadcast.photo:
            await bot.send_photo(
                tg_id, broadcast.photo, caption=text)
        elif broadcast.video:
            await bot.send_video(
                tg_id, broadcast.video, caption=text)
        else:
            await bot.send_message(tg_id, text, disable_web_page_preview=True)
