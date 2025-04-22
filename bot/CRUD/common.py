import math

from asgiref.sync import sync_to_async
from django.db.models import Avg
from django.utils.timezone import now, timedelta
from bot.utils.certs import create_cert_img
from inwork import models as mdl
from pathlib import Path
from django.core.files import File

DELTA_VISITS = 110


@sync_to_async()
def update_visit_journal(record_id, params):
    '''Обновлении информации о записи в журнале на услуги'''
    visit = mdl.VisitJournal.objects.filter(id=record_id)
    visit.update(**params)
    visit = visit.first()
    avg_rate = mdl.VisitJournal.objects.filter(visit_master=visit.visit_master).aggregate(
        avg=Avg('estimation'))['avg'] or visit.visit_master.rate
    visit.visit_master.rate = math.floor(avg_rate * 10) / 10
    visit.visit_master.save()


@sync_to_async()
def select_open_recors():
    '''Получить все записи клиентов, где дата больше чем сейчас + 110мин.
    Не завершенные, не отмененные, бот не заблокирован
    '''
    visits = mdl.VisitJournal.objects.filter(
        finish=False, cancel=False,
    ).exclude(
        visit_client__is_blocked=True,
        visit_client__tg_id__isnull=True)
    return [
        (
            visit.id,
            visit.date,
            visit.visit_master.name.name.split(' - ')[0],
            visit.visit_client.name,
            visit.visit_client.tg_id,
            visit.visit_service,
            visit.visit_service.duration,
            visit.visit_service.price,
            visit.confirmation,
            visit.visit_client.phone,
        )
        for visit in visits]


@sync_to_async()
def get_certificates():
    '''Получить сертификаты'''
    certificates = mdl.Certificate.objects.order_by('id')[:4]
    return [certificate for certificate in certificates]


@sync_to_async()
def get_certificate(id):
    '''Получить сертификат'''
    certificate = mdl.Certificate.objects.filter(id=id).first()
    return certificate


@sync_to_async()
def set_certificate(price: int):
    # путь к файлу изображения
    name = f"Подарочный сертификат на {price} рублей"
    description = name

    # Пытаемся найти сертификат по цене
    certificate, created = mdl.Certificate.objects.get_or_create(
        price=price,
        defaults={
            "name": name,
            "description": description,
        }
    )

    return certificate


@sync_to_async()
def set_shopping_entry(tg_id, certificate_id, email):
    '''Запись в журнале покупок'''
    client = mdl.Client.objects.filter(tg_id=tg_id).first()
    certificate = mdl.Certificate.objects.filter(id=certificate_id).first()
    new_entry = mdl.ShoppingJournal.objects.create(
        client=client, client_cert=certificate, email=email)

    return {
        'client': client,
        'certificate': certificate,
        'new_entry': new_entry
    }


@sync_to_async()
def get_shopping_entry(tg_id):
    '''Запись в журнале покупок'''
    client = mdl.Client.objects.filter(tg_id=tg_id).first()
    shopping_entry = mdl.ShoppingJournal.objects.filter(client=client).first()
    img_buffer = create_cert_img(shopping_entry, shopping_entry.client_cert)

    return shopping_entry, img_buffer
