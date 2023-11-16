from asgiref.sync import sync_to_async
from inwork import models as mdl

# проверка нового пользователя
@sync_to_async()
def check_for_newbie(telegram_id):
    client = mdl.Client.objects.filter(telegram_id=telegram_id).first()
    # если не новый, то записываем его телеграм ID в бд
    if not client:
        mdl.Client.objects.create(telegram_id=telegram_id)
        return True
    # на случай, если новый, но решил ещё раз вызвать команду /start
    if client.name == 'newbie':
        return True
    return False

# запись имени в бд
@sync_to_async()
def set_name(telegram_id, name):
    client = mdl.Client.objects.filter(telegram_id=telegram_id).first()
    client.name = name
    client.save()


# запись телефона в бд
@sync_to_async()
def set_phone(telegram_id, phone):
    client = mdl.Client.objects.filter(telegram_id=telegram_id).first()
    client.phone = phone
    client.save()