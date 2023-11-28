from re import sub


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
