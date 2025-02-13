from asgiref.sync import sync_to_async
from django.db.models import Min
from django.db.models.functions import TruncDate
from datetime import date

from inwork import models as mdl


@sync_to_async()
def check_master(tg_id):
    '''Проверка, существования мастера по tg_id
    вернуть ID клиента (мастера)'''
    master = mdl.Master.objects.filter(name__tg_id=tg_id).first()
    if master:
        # вернуть ID клиента (мастера)
        return (master.name.id, True)
    return (master, False)


@sync_to_async()
def get_master_work_on_date(tg_id, date):
    '''Получение работ мастера на определенную дату'''
    visits = mdl.VisitJournal.objects.annotate(
        onlydate=TruncDate('date')).filter(
            onlydate=date,
            finish=False,
            cancel=False,
            visit_master__name__tg_id=tg_id,
    ).order_by('-date')
    if not visits:
        return False

    return [
        (
            visit.id,
            visit.date,
            visit.visit_client.name,
            visit.visit_service,
            visit.visit_service.duration,
            visit.visit_service.price,
        )
        for visit in visits]


@sync_to_async()
def get_dates_master_records(tg_id):
    '''Получить даты с открытыми записями мастера'''
    today = date.today()
    visits = mdl.VisitJournal.objects.annotate(
        onlydate=TruncDate('date')  # Обрезаем время, оставляем только дату
    ).filter(
        finish=False,
        onlydate__gte=today,  # Показываем визиты с сегодняшней даты
        visit_master__name__tg_id=tg_id
    ).values('onlydate').distinct().order_by('-onlydate')  # Уникальные только даты

    if not visits:
        return False

    # Получаем минимальную дату по уникальным дням
    visits = visits.annotate(
        min_date=Min('onlydate')
    ).values_list('min_date', flat=True)

    return [visit.strftime('%d-%m-%Y') for visit in visits]
