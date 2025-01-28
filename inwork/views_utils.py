from hashlib import sha1
import inwork.models as md
from datetime import datetime as dt
from datetime import timedelta as td


def edit_start_time(now, start_time):
    '''Корректировка времени старта с учётом текущего времени'''
    minutes_now = now.minute
    hour_now = now.hour

    # округляем до 15 минут текущее время
    if 0 <= minutes_now < 15:
        round_for = 15
    elif 15 <= minutes_now < 30:
        round_for = 30
    elif 30 <= minutes_now < 45:
        round_for = 45
    elif 45 <= minutes_now:
        round_for = 0

    # больше ли текущее время
    # чем время начала рабочего дня
    if start_time > now:
        now = start_time
    else:
        now = now

    # обозначаем время старта отсчёта
    if round_for != 0:
        start_time = now.replace(
            minute=round_for, second=0, microsecond=0)
    else:
        start_time = now.replace(
            hour=hour_now+1, minute=round_for, second=0, microsecond=0)

    return start_time


def get_free_times(**kwargs):
    """
    Найти доступные слоты времени для записи на услугу.

    :param visits: список визитов [(start_time, duration_in_minutes)]
    :param selected_date: дата, для которой ищем доступные слоты (datetime")
    :param work_start: начало рабочего дня (datetime.time)
    :param work_end: конец рабочего дня (datetime.time)
    :param service_duration: длительность новой услуги в минутах (int)
    :return: список доступных временных слотов [datetime.time]
    """
    visits = kwargs.get('visits')
    selected_date = kwargs.get('selected_date')
    work_start = kwargs.get('work_start')
    work_end = kwargs.get('work_end')
    service_duration = kwargs.get('service_duration')

    # Получаем текущее время
    now = dt.now()

    # Если выбранная дата раньше текущей, возвращаем пустой список
    if selected_date < now.date():
        return []

    # Если дата равна текущей, учитываем текущее время как ограничение
    if selected_date == now.date():
        start_time_combine = dt.combine(selected_date, work_start)
        start_time = edit_start_time(now, start_time_combine)
    else:
        start_time = dt.combine(selected_date, dt.min.time())

    # Преобразуем визиты в занятые интервалы (start_time, end_time)
    busy_intervals = []
    for visit_start_time, duration in visits:
        # Преобразуем время визита в объект datetime
        visit_start_dt = dt.combine(selected_date, visit_start_time)
        visit_end_dt = visit_start_dt + td(minutes=duration)
        busy_intervals.append((visit_start_dt, visit_end_dt))

    # Добавляем начало и конец рабочего дня
    work_start_dt = dt.combine(selected_date, work_start)
    work_end_dt = dt.combine(selected_date, work_end)

    # Сортируем интервалы
    busy_intervals.sort()

    # Объединяем пересекающиеся и смежные интервалы
    merged_intervals = []
    for start, end in busy_intervals:
        if merged_intervals and merged_intervals[-1][1] >= start:
            merged_intervals[-1] = (merged_intervals[-1]
                                    [0], max(merged_intervals[-1][1], end))
        else:
            merged_intervals.append((start, end))

    # Проверяем каждый временной слот (с шагом 15 минут)
    available_slots = []
    current_time = start_time.replace(second=0, microsecond=0)

    # Убедимся, что проверяем время только в пределах рабочего дня
    while current_time + td(minutes=service_duration) <= work_end_dt:
        # Время окончания услуги
        service_end_time = current_time + td(minutes=service_duration)

        # Проверяем, пересекается ли текущий слот с занятыми интервалами
        is_free = all(not (current_time < end and service_end_time > start)
                      for start, end in merged_intervals)

        # Если слот свободен, добавляем его в доступные
        if is_free:
            # Убедимся, что слот находится в пределах рабочего дня
            if current_time >= work_start_dt and service_end_time <= work_end_dt:
                available_slots.append(current_time.time())

        # Переходим к следующему 15-минутному слоту
        current_time += td(minutes=15)

    return available_slots


def find_available_time_for_all_days(master_id, service_id):
    '''Расчет времени для всех дней расписания мастера
    :param master_id: айдишник мастера в бд
    :param service_id: айдишник услуги в бд
    :param selected_date: выбранная дата автоматически(сегодняшний день) или вручную
    :return: список словарей с датой и доступными временными слотами [{
    'date': date,
    'free_times': [datetime.time]}]
    '''
    master = md.Master.objects.filter(id=master_id).first()
    service = md.Service.objects.filter(id=service_id).first()
    service_duration = service.duration
    selected_date = dt.now().date()

    # получаем все рабочие дни от выбранной даты и далее
    schedule_days = md.MasterSchedule.objects.filter(
        master=master,
        date__gte=selected_date).order_by(
            'date').distinct()

    # достаём всё свободное время из каждого рабочего дня
    master_schedule = []
    for day in schedule_days:
        existing_visits = md.VisitJournal.objects.filter(
            visit_master=master,
            date=day.date,
            finish=False, cancel=False).order_by('date')

        visits = [(visit.date.time(), visit.visit_service.duration)
                  for visit in existing_visits]

        free_times = get_free_times(visits=visits,
                                    selected_date=day.date,
                                    work_start=day.start_time,
                                    work_end=day.end_time,
                                    service_duration=service_duration)
        master_schedule.append({
            'date': day.date,
            'free_times': free_times

        })

    return {
        'master_id': master.id,
        'service_id': service.id,
        'master_schedule': master_schedule
    }
