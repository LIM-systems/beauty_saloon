import json
from re import sub
from datetime import datetime
from aiogram import types
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from bot.CRUD import client as sqlc
from bot.utils import keyboards as kb

import env


class ClientLastVisitMiddleware(LifetimeControllerMiddleware):
    '''Запись времени посещения бота при любых действиях клиента'''
    skip_patterns = ['error', 'update']

    async def post_process(self, query: types.CallbackQuery, data, *args):
        '''Исполняется после хендлера'''
        # записываем информацию о последнем визите пользователя в базу данных
        await sqlc.update_client(
            tg_id=query.from_user.id,
            params={'last_visit': datetime.now()}
        )


def clean_phone(phone):
    '''Очистка номера от лишних символов
    и приведение номеров к общему синтаксису +7'''
    clear = sub('\D', '', phone)
    if clear.startswith('7') and len(clear) == 11:
        clear = f'+{clear}'
    elif clear.startswith('9') and len(clear) == 10:
        clear = f'+7{clear}'
    elif clear.startswith('8') and len(clear) == 11:
        clear = f'+7{clear[1:]}'
    else:
        return False
    return clear


async def alert_admins_msg(visit_id, text):
    '''Оповещение админов'''
    visit = await sqlc.get_client_record(visit_id)
    return f'''
<a href="{env.BASE_URL}admin/inwork/visitjournal/{visit_id}">
{text} </a>
Клиент: <b>{visit[7]}</b> <code>{visit[8]}</code>
Мастер: <b>{visit[2]}</b>
Услуга: <b>{visit[3]}</b>
Время: <b>{visit[1].strftime('%Y-%m-%d %H:%M')}</b>
'''


async def alert_master_msg(visit_id, text):
    '''Оповещение мастера'''
    visit = await sqlc.get_client_record(visit_id)
    master__tg_id = visit[2].tg_id
    return (master__tg_id, f'''
<b>{text}</b>

Клиент: <b>{visit[7]}</b>
Услуга: <b>{visit[3]}</b>
Время: <b>{visit[1].strftime('%Y-%m-%d %H:%M')}</b>
''')


async def create_invoice(certificate, bot, user_tg_id):
    '''Создать инвойс'''
    price = types.LabeledPrice(
        label=certificate.name, amount=certificate.price * 100)
    provider_data = json.dumps({
        'receipt': {
            'items': [{
                'description': f'{certificate.name}',
                'quantity': '1.00',
                'amount': {
                    'value': f'{certificate.price}.00',
                    'currency': 'RUB'
                },
                'vat_code': 1,
                "payment_mode": "full_payment",
                "payment_subject": "commodity"
            }]
        }
    })
    await bot.send_invoice(user_tg_id,
                           title=f'Покупка {certificate.name}',
                           description=f'{certificate.description}',
                           start_parameter='start_parameter',
                           provider_token=env.PAYMENT_TOKEN,
                           prices=[price],
                           currency='RUB',
                           need_email=True,
                           send_email_to_provider=True,
                           payload=f'{certificate.id}',
                           provider_data=provider_data
                           )
