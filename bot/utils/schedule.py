import asyncio
import base64
import json
import os
from datetime import datetime as dt
from datetime import timedelta as td
from random import choice

import aiohttp
import aioschedule
from aiogram.utils.exceptions import BotBlocked, UserDeactivated

import bot.CRUD.client as sqlc
from bot.loader import bot, logger


async def get_temp_notifications():
    '''Получим все временные уведомления для рассылки,
    вышлем уведомления клиентам
    и удалим запись после отправки'''
    notifications = await sqlc.get_temp_notification()

    for note in notifications:
        # время уведомления клиента с учетом часового пояса Django
        user_time = dt.astimezone(note[4])
        # + и - 30 cек от времени клиента
        tdelta_plus = user_time + td(seconds=30)
        tdelta_minus = user_time - td(seconds=30)
        time_now = dt.now().time()
        date_now = dt.now().date()
        dt_now = dt.combine(date_now, time_now)
        tdelta_plus_cb = dt.combine(tdelta_plus.date(), tdelta_plus.time())
        tdelta_minus_cb = dt.combine(tdelta_minus.date(), tdelta_minus.time())

        # если дата-время входит в промежуток данной минуты добавим в список
        # или если дата-время меньше чем сейчас (защита от пропущенных)
        if (tdelta_minus_cb < dt_now < tdelta_plus_cb
           or user_time.combine(user_time.date(), user_time.time()) < dt_now):
            tg_id = note[0]
            video_id = note[1]
            video_name = note[2]
            training_day = note[3]
            # отправка уведомления о занятии
            if training_day:  # после тренировки дня
                callback = f'after_/{video_id}/td'
            else:  # после любой тренировки кроме дня
                callback = f'after_/{video_id}'
            # отправка клиенту
            try:
                # не дожидаясь ответа клиента отметим тренировку как пройденную
                trainlog_id = await sql.add_training_log(tg_id, video_id)
                await bot.send_message(
                    tg_id, f'Позанимались по уроку <b>{video_name}</b>?',
                    reply_markup=kb.inline_btns(
                        after_training, f'{callback}/{trainlog_id}'))
            except BotBlocked:
                logger.error(f'{tg_id} - пользователь заблокировал бота')
                # Удалим все уведомления если пользователь заблочил бота
                await sheduler.clear_notifications(tg_id)
            except UserDeactivated:
                logger.error(f'{tg_id} - пользователь деактивирован')
                # Удалим все уведомления если пользователь деактивирован
                await sheduler.clear_notifications(tg_id)
            except Exception as e:
                logger.error(
                    f'Ошибка при отправке сообщения для {tg_id} - {e}')

            await asyncio.sleep(0.2)
            # после отправки удалим запись
            await sheduler.delete_temp_notification(note[5])
