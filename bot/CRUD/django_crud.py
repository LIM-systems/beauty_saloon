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
    print(params)
    if 'phone' in params:
        check_user = mdl.Client.objects.filter(phone=params.get('phone'))
        if check_user:
            check_user.update(tg_id=tg_id, name=params.get('name'))
        return 'update_phone'
    mdl.Client.objects.update_or_create(
        tg_id=tg_id, defaults=params
    )
