from datetime import datetime as dt, timedelta as td, time

from django.template.defaulttags import comment

import inwork.models as md

import logging

logger = logging.getLogger('main')


def find_available_time(master_id, service_id, planned_date, selected_time, masters_data):
    # Получаем расписание мастера на выбранный день
    master_schedule = md.MasterSchedule.objects.filter(
        master__id=master_id, date=planned_date).first()

    service_duration = md.Service.objects.filter(
        id=service_id).first().duration

    if not master_schedule:
        # Если нет расписания на выбранный день, вернем []
        return []

    if selected_time:
        if len(selected_time.split(' ')) == 2:
            selected_time = dt.strptime(selected_time, '%Y-%m-%d %H:%M')
        else:
            selected_time = None

    busy_times = []

    if masters_data:
        for data in masters_data:
            datetimes = [dt.combine(planned_date, dt.strptime(
                time, '%H:%M').time()) for time in data]
            start_time_data = datetimes[0] - td(minutes=service_duration)
            new_data_times = []
            while start_time_data <= datetimes[-1]:
                new_data_times.append(start_time_data)
                start_time_data += td(minutes=15)
            busy_times.append(new_data_times)

    start_time = dt.combine(planned_date, master_schedule.start_time)
    end_time = dt.combine(planned_date, master_schedule.end_time)

    # для сегодня берем время сейчас + выровнять до 0 или 15ти кратным минутам
    if planned_date == dt.now().date():
        minutes_now = dt.now().minute
        hour_now = dt.now().hour
        if 0 <= minutes_now < 15:
            round_for = 15
        elif 15 <= minutes_now < 30:
            round_for = 30
        elif 30 <= minutes_now < 45:
            round_for = 45
        elif 45 <= minutes_now:
            round_for = 0
        if start_time > dt.now():
            now = start_time
        else:
            now = dt.now()
        if round_for != 0:
            start_time = now.replace(
                minute=round_for, second=0, microsecond=0)
        else:
            start_time = now.replace(
                hour=hour_now+1, minute=round_for, second=0, microsecond=0)

    # Получаем все записи в журнале для выбранного мастера и дня
    existing_visits = md.VisitJournal.objects.filter(
        visit_master__id=master_id,
        date__gte=start_time - td(minutes=180),
        date__lte=end_time,
        finish=False, cancel=False).order_by('date')

    debug_date = dt.strptime('2024-06-07', '%Y-%m-%d').date()

    # Ищем свободное время для записи
    current_time = start_time
    available_times = []
    not_available_times = []
    # пока текущее время + длительность услуги меньше конца рабочего дня
    while current_time + td(minutes=service_duration) <= end_time:
        # Проверяем, свободно ли время

        is_time_free = True

        for visit in existing_visits:
            if visit.math_value and visit.math_action == 'plus':
                visit_end_time = visit.date + \
                    td(minutes=(visit.visit_service.duration + visit.math_value))
            elif visit.math_value and visit.math_action == 'minus':
                visit_end_time = visit.date + \
                    td(minutes=(visit.visit_service.duration - visit.math_value))
            else:
                visit_end_time = visit.date + \
                    td(minutes=visit.visit_service.duration)

            current_end_time = current_time + td(minutes=service_duration)
            if (visit.date <= current_time < visit_end_time or
                visit.date < current_end_time <= visit_end_time or
                    (current_time < visit.date and current_end_time > visit_end_time)):
                is_time_free = False
                break

        if current_time == selected_time:
            time_count = current_time
            while time_count < current_time + td(minutes=service_duration):
                not_available_times.append(time_count)
                time_count += td(minutes=15)

        if is_time_free:
            if busy_times:
                is_available = True
                for data in busy_times:
                    if current_time in data or current_time in not_available_times:
                        is_available = False
                if is_available:
                    available_times.append(current_time)
            else:
                available_times.append(current_time)
        current_time += td(minutes=15)

    available_times = {
        'render_times': available_times,
        'busy_times': not_available_times
    }
    return available_times


def find_available_time_for_all_days(master_id, service_id, selected_time, masters_data, all):
    '''Расчет времени для всех дней расписания мастера'''
    # Получаем все дни, для которых есть расписание
    if all:
        schedule_days = md.MasterSchedule.objects.filter(
            master__id=master_id,
            date__gte=dt.now().date()).order_by(
                'date').values_list('date', flat=True).distinct()
    else:
        selected = selected_time.split(' ')
        if len(selected) == 2:
            selected_date = dt.strptime(selected_time, '%Y-%m-%d %H:%M').date()
        else:
            selected_date = dt.strptime(selected_time, '%Y-%m-%d').date()
        schedule_days = md.MasterSchedule.objects.filter(
            master__id=master_id, date=selected_date).values_list('date',
                                                                  flat=True)

    result = []
    for planned_date in schedule_days:
        available_times = find_available_time(
            master_id, service_id, planned_date, selected_time, masters_data)
        render_times = [time.strftime('%H:%M')
                        for time in available_times.get('render_times')]
        available_times['render_times'] = render_times
        busy_times = [time.strftime('%H:%M')
                      for time in available_times.get('busy_times')]
        available_times['busy_times'] = busy_times

        result.append({
            "date": planned_date.strftime('%Y-%m-%d'),
            "times": available_times
        })

    return {"schedule": result}


START_WORK_TIME_DEFAULT = '10:00:00'
END_WORK_TIME_DEFAULT = '21:00:00'


def round_time_down(input_time):
    # Округление времени вниз до ближайшей половины часа
    if input_time.minute in (15, 45):
        return input_time.replace(minute=input_time.minute - 15)
    else:
        return input_time


def round_time_up(input_time):
    # Округление времени вверх до ближайшей половины часа
    if 0 < input_time.minute < 15:
        return input_time.replace(minute=15, second=0, microsecond=0)
    elif 15 < input_time.minute < 30:
        return input_time.replace(minute=30, second=0, microsecond=0)
    elif 30 < input_time.minute < 45:
        return input_time.replace(minute=45, second=0, microsecond=0)
    elif 45 < input_time.minute:
        return input_time.replace(minute=0, second=0, microsecond=0) + td(hours=1)
    else:
        return input_time
    # if input_time.minute in (45,):
    #     return input_time.replace(minute=0, second=0, microsecond=0) + td(hours=1)
    # elif input_time.minute in (15,):
    #     return input_time.replace(minute=input_time.minute + 15)
    # else:
    #     return input_time


def get_master_schedule(master, date, visits, admin=False):
    '''Получение расписания мастера на выбранный день'''
    name = master.name.name
    phone = master.name.phone
    master_date = md.MasterSchedule.objects.filter(
        date=date, master=master).first()
    is_weekend = False
    if master_date:
        start_time = master_date.start_time.strftime('%H:%M')
        end_time = master_date.end_time.strftime('%H:%M')
    else:
        is_weekend = True
        start_time = START_WORK_TIME_DEFAULT
        end_time = END_WORK_TIME_DEFAULT
    visits_db = visits.filter(visit_master=master).all()
    visits_list = []
    for visit in visits_db:
        client_id = visit.visit_client.id
        client = visit.visit_client.name
        visit_name = visit.visit_service.name
        client_phone = visit.visit_client.phone if admin else None
        comment = visit.description
        visit_confirm = visit.confirmation
        if visit.math_value:
            if visit.math_action == 'plus':
                visit_duration = visit.visit_service.duration + visit.math_value
            elif visit.math_action == 'minus':
                visit_duration = visit.visit_service.duration - visit.math_value
        else:
            visit_duration = visit.visit_service.duration
        delta = td(minutes=visit_duration)
        visit_time_start = visit.date.time()
        visit_time_end = (dt.combine(
            dt.today(), visit_time_start) + delta).time()
        rounded_start_time = round_time_up(
            dt.combine(dt.today(), visit_time_start)).time()
        rounded_end_time = round_time_up(
            dt.combine(dt.today(), visit_time_end)).time()
        end_work_master = time(21, 0)
        if end_work_master < rounded_end_time:
            rounded_end_time = end_work_master
        visit_time_start = rounded_start_time.strftime('%H:%M')
        visit_time_end = rounded_end_time.strftime('%H:%M')
        visits_list.append({
            'id': client_id,
            'client': client,
            'time_start': visit_time_start,
            'time_end': visit_time_end,
            'visit_name': visit_name,
            'visit_confirm': visit_confirm,
            'client_phone': client_phone,
            'comment': comment
        })
    return {
        'name': name,
        'phone': phone,
        'start_time': start_time,
        'end_time': end_time,
        'is_weekend': is_weekend,
        'visits': visits_list
    }
