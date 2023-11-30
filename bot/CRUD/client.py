from asgiref.sync import sync_to_async

from inwork import models as mdl


@sync_to_async()
def check_for_newbie(tg_id, name):
    '''проверка нового пользователя'''
    client = mdl.Client.objects.filter(tg_id=tg_id).first()
    # если не новый, то записываем его телеграм ID в бд
    if not client:
        # mdl.Client.objects.create(tg_id=tg_id, name=name)
        return True
    return False


@sync_to_async()
def update_client(tg_id, params):
    '''Обновлении информации о клиенте или создание клиента'''
    # если передан телефон, клиенту добавляем tg_id
    # это даст возможность зарегать клиента заведенного вручную по номеру телефона
    if 'phone' in params:
        check_user = mdl.Client.objects.filter(phone=params.get('phone'))
        if check_user:
            check_user.update(tg_id=tg_id, name=params.get('name'))
        return 'update_phone'
    mdl.Client.objects.update_or_create(
        tg_id=tg_id, defaults=params
    )


@sync_to_async()
def check_client_recors(tg_id):
    '''Проверка существования записей клиента'''
    result = {}
    visits = mdl.VisitJournal.objects.filter(
            visit_client__tg_id=tg_id,
                ).order_by('-date')
    if visits.filter(finish=False, cancel=False):
        result['not_finish'] = True

    if visits.filter(finish=True, cancel=False):
        result['finish'] = True

    return result


@sync_to_async()
def select_client_recors(tg_id, finish, cancel=False, limit=10):
    '''Выборка записей клиента'''
    visits = mdl.VisitJournal.objects.filter(
            visit_client__tg_id=tg_id,
            finish=finish,
            cancel=cancel,
        ).order_by('-date')[:limit]
    return [
        (
            visit.id,
            visit.date,
            visit.visit_master.name,
            visit.visit_service,
            visit.visit_service.duration,
            visit.visit_service.price,
            visit.estimation,
        )
        for visit in visits]


@sync_to_async()
def get_client_record(record_id):
    '''Получить одну запись клиента по id'''
    visit = mdl.VisitJournal.objects.get(id=record_id)
    return (
            visit.id,
            visit.date,
            visit.visit_master.name,
            visit.visit_service,
            visit.visit_service.duration,
            visit.visit_service.price,
            visit.estimation,
        )


@sync_to_async()
def delete_client_record(record_id):
    '''Удалить одну запись клиента по id'''
    mdl.VisitJournal.objects.get(id=record_id).delete()