from django.utils.timezone import now, timedelta
from asgiref.sync import sync_to_async

from inwork import models as mdl


DELTA_VISITS = 110


@sync_to_async()
def update_visit_journal(record_id, params):
    '''Обновлении информации о записи в журнале на услуги'''
    mdl.VisitJournal.objects.filter(id=record_id).update(**params)


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
            visit.visit_master.name,
            visit.visit_client.name,
            visit.visit_client.tg_id,
            visit.visit_service,
            visit.visit_service.duration,
            visit.visit_service.price,
            visit.confirmation,
            visit.visit_client.phone,
        )
        for visit in visits]
