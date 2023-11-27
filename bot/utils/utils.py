from aiogram import types


# получение имени из телеграма
async def get_telegram_name(user):
    if not user.first_name:
        name = user.last_name
    elif not user.last_name:
        name = user.first_name
    else:
        name = user.first_name + " " + user.last_name
    return name
