from datetime import datetime as dt, timedelta as td

import inwork.models as md


def find_available_time(master_id, services_duration, planned_date):
    # Получаем расписание мастера на выбранный день
    master_schedule = md.MasterSchedule.objects.filter(
        master__id=master_id, date=planned_date).first()

    if not master_schedule:
        # Если нет расписания на выбранный день, вернем []
        return []

    start_time = dt.combine(planned_date, master_schedule.start_time)
    end_time = dt.combine(planned_date, master_schedule.end_time)
    # для сегодня берем время сейчас + выровнять до 0 или 30мин
    if planned_date == dt.now().date():
        minutes_now = dt.now().minute
        if minutes_now >= 30:
            start_time = (dt.now() + td(minutes=30)).replace(
                minute=0, second=0, microsecond=0)
        elif minutes_now >= 0:
            start_time = dt.now().replace(minute=30, second=0, microsecond=0)
    print(start_time)

    # Получаем все записи в журнале для выбранного мастера и дня
    existing_visits = md.VisitJournal.objects.filter(
        visit_master__id=master_id,
        date__gte=start_time - td(minutes=180),
        date__lte=end_time,
        finish=False, cancel=False).order_by('date')

    # Ищем свободное время для записи
    current_time = start_time
    available_times = []
    # пока текущее время + длительность услуги меньше конца рабочего дня
    while current_time + td(minutes=services_duration) <= end_time:
        # Проверяем, свободно ли время
        is_time_free = all(
            visit.date + td(minutes=visit.visit_service.duration) <= current_time or
            current_time + td(minutes=services_duration) <= visit.date
            for visit in existing_visits
        )

        if is_time_free:
            available_times.append(current_time)
        # Переходим к следующему времени с шагом 30 минут
        current_time += td(minutes=30)

    return available_times


def find_available_time_for_all_days(master_id, services_id):
    '''Расчет времени для всех дней расписания мастера'''
    services = md.Service.objects.filter(
        id__in=services_id).values_list('duration', flat=True)
    # Получаем все дни, для которых есть расписание
    schedule_days = md.MasterSchedule.objects.filter(
        master__id=master_id,
        date__gte=dt.now().date()).order_by(
            'date').values_list('date', flat=True).distinct()

    result = []

    for planned_date in schedule_days:
        available_times = find_available_time(
            master_id, sum(services), planned_date)
        result.append({
            "date": planned_date.strftime('%Y-%m-%d'),
            "free_times": [time.strftime('%H:%M') for time in available_times]
        })

    return {"schedule": result}
