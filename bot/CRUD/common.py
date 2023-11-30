from asgiref.sync import sync_to_async

from inwork import models as mdl


@sync_to_async()
def update_visit_journal(record_id, params):
    '''Обновлении информации о записи в журнале на услуги'''
    mdl.VisitJournal.objects.filter(id=record_id).update(**params)
