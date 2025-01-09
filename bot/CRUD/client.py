from asgiref.sync import sync_to_async

from inwork import models as mdl


@sync_to_async()
def check_for_newbie(tg_id, name):
    '''проверка нового пользователя'''
    client = mdl.Client.objects.filter(tg_id=tg_id).first()
    # если не новый, то записываем его телеграм ID в бд
    if client:
        return client.id
    return False


@sync_to_async()
def create_or_update_client(tg_id, params):
    '''Обновлении информации о клиенте или создание клиента'''
    # если передан телефон, клиенту добавляем tg_id
    # это даст возможность зарегать клиента заведенного вручную по номеру телефона
    if 'phone' in params:
        check_user = mdl.Client.objects.filter(phone=params.get('phone'))
        if check_user:
            check_user.update(tg_id=tg_id, name=params.get('name'))
            return (check_user.first().id, 'update_phone')
    client = mdl.Client.objects.update_or_create(
        tg_id=tg_id, defaults=params
    )
    return (client[0].id, True)


@sync_to_async()
def get_user_info(tg_id):
    '''Получить данные клиента для профиля'''
    user = mdl.Client.objects.filter(tg_id=tg_id).first()
    return {
        'id': user.id,
        'name': user.name,
        'phone': user.phone,
    }


@sync_to_async()
def update_client(tg_id, params):
    '''Обновлении информации о клиенте или создание клиента'''
    client = mdl.Client.objects.filter(tg_id=tg_id)
    if client:
        client.update(**params)
        return client.first().id


@sync_to_async()
def check_client_recors(tg_id):
    '''Проверка существования записей клиента'''
    visits = mdl.VisitJournal.objects.filter(
        visit_client__tg_id=tg_id,
        finish=False,
        cancel=False
    ).order_by('-date')

    return [visit for visit in visits]


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
            visit.visit_master.name.name.split(' - ')[0],
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
        visit.visit_master.name.name.split(' - ')[0],
        visit.visit_service,
        visit.visit_service.duration,
        visit.visit_service.price,
        visit.estimation,
        visit.visit_client.name,
        visit.visit_client.phone,
        visit.confirmation,
    )


@sync_to_async()
def get_client_record_with_bad_estimate(tg_id):
    '''Поиск последней записи клиента с плохой оценкой'''
    visit = mdl.VisitJournal.objects.filter(
        visit_client__tg_id=tg_id,
        cancel=False,
        finish=True,
        estimation__lte=3).order_by('-date').first()
    if visit:
        return visit.id
