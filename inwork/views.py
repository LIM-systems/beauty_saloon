import logging
from datetime import date
from datetime import datetime as dt
from datetime import timedelta as td

import requests
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from env import BASE_URL, CHAT_ADMINS, TOKEN
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from typing import List, Dict

import inwork.models as md
from inwork.utils import (END_WORK_TIME_DEFAULT, START_WORK_TIME_DEFAULT,
                          get_master_schedule)
from inwork.views_utils import find_available_time_for_all_days

logger = logging.getLogger('main')


class APICSRFToken(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({'token': get_token(request)}, status=200)


class APIGetCategories(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Получить все категории с учетом персон'''
        result = {'categories': []}
        persons: list = request.data.get('persons')
        if not persons:
            persons = md.Person.objects.all().values_list('title', flat=True)
        categories = md.Service.objects.filter(
            persons__title__in=persons
        ).values_list('categories__id', 'categories__name')
        for id_, name in categories:
            if name not in str(result):
                result['categories'].append({'id': id_, 'name': name})
        return Response(result, status=status.HTTP_200_OK)


class APIGetServices(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Вернуть услуги по полученному списку категорий'''
        categories = request.data.get('categories')
        persons = request.data.get('persons')
        services = md.Service.objects.filter(
            categories__in=categories,
            persons__title__in=persons).values(
                'id', 'name', 'description', 'price', 'duration', 'image')
        if not services:
            return Response(
                {'nodata': 'Услуг по выбранным категориям не найдено'},
                status=status.HTTP_204_NO_CONTENT)
        services_data = []
        for service in services:
            if service not in services_data:
                services_data.append(service)
        return Response({'services': services_data}, status=status.HTTP_200_OK)


class APIGetMasters(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Получить мастеров по выбранным услугам'''
        services = request.data.get('services')
        masters = md.Master.objects.filter(
            services__in=services).distinct().values(
                'id', 'name__name', 'description', 'services', 'rate')
        if not masters:
            return Response(
                {'nodata': 'Мастеров по выбранным услугам не найдено'},
                status=status.HTTP_204_NO_CONTENT)
        services_data = {}
        for service_id in services:
            service = md.Service.objects.filter(id=service_id).first()
            masters = md.Master.objects.filter(services=service).values(
                'id', 'name__name', 'description', 'rate'
            )
            id = service.id
            services_data[id] = {
                'id': id,
                'name': service.name,
            }
            if masters:
                services_data[id]['masters'] = masters
            else:
                services_data[id]['masters'] = None
        result_list = list(services_data.values())
        return Response({'masters': result_list}, status=status.HTTP_200_OK)


class APIGetMasterSchedule(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Получить свободное время для выбранного мастера на ближайшие дни'''
        master_id: int = request.data.get('master_id')
        service_id: int = request.data.get('service_id')
        response = find_available_time_for_all_days(
            master_id, service_id)
        return Response(response, status=status.HTTP_200_OK)


class APICreateRecords(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Создать запись(и) в журнале'''
        try:
            # достаём данные из запроса
            user_id: int = request.data.get('user_id')
            client = md.Client.objects.get(id=user_id)
            orders: List[Dict[str, str]] = request.data.get('orders')

            bad_orders = []
            valid_orders = []
            for order in orders:
                # достаём данные каждого ордера
                master_id = order.get('master_id')
                service_id = order.get('service_id')
                day = order.get('day')
                time = order.get('time')

                # получаем необходимое из бд
                # и делаем проверку доступности выбранной даты и времени
                master = md.Master.objects.get(id=master_id)
                service = md.Service.objects.get(id=service_id)
                date_obj = dt.strptime(day, "%d.%m.%Y").date()
                time_obj = dt.strptime(time, "%H:%M").time()

                # вычисляем всё нужное время
                start_datetime = dt.combine(date_obj, time_obj)
                end_datetime = start_datetime + td(minutes=service.duration)
                intervals = list(
                    (start_datetime + td(minutes=15 * i)).time()
                    for i in range((end_datetime - start_datetime).seconds // 900)
                )

                # достаём свободное, что есть по факту
                available_all_times = find_available_time_for_all_days(
                    master_id, service_id, selected_date=date_obj)

                # сравниваем свободное и доступное
                all_are_available = True
                for available_time in available_all_times.get('master_schedule'):
                    date = available_time.get('date')
                    times = available_time.get('free_times')
                    if date_obj == date:
                        for interval in intervals:
                            if interval not in times:
                                all_are_available = False
                                break
                        break

                # записываем id услуги в список плохих заказов
                # если выбранное время уже занято
                if not all_are_available:
                    bad_orders.append(service_id)
                # создаём запись в бд, если всё ок
                else:
                    valid_orders.append((master, service, start_datetime))

            if (bad_orders):
                return Response({'response': bad_orders}, status=status.HTTP_200_OK)
            else:
                for valid_order in valid_orders:
                    master, service, start_datetime = valid_order
                    visit = md.VisitJournal.objects.create(
                        visit_client=client,
                        visit_master=master,
                        visit_service=service,
                        date=start_datetime,
                    )
                    URL = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'

                    # отправка уведомления в чат админов
                    text = f'📝<b>Новая запись!</b>\nКлиент: <b>{client.name}</b>\n'
                    text += f'\n\n🟢<b>Мастер: {master.name.name}</b>'
                    text += f'''
Услуга: <b>{service.name}</b>
Время: <b>{start_datetime}</b>
'''
                    text += f'''
<a href="{BASE_URL}admin/inwork/visitjournal/{visit.id}/change/">Запись в журнале</a>'''
                    data_admin = {
                        'chat_id': CHAT_ADMINS,
                        'parse_mode': 'HTML',
                        'text': text}
                    requests.post(URL, data=data_admin)

                    # отправка уведомления в чат мастера
                    text = f'📝<b>Новая запись!</b>\nКлиент: <b>{client.name}</b>\n'
                    text = f'''
Услуга: <b>{service.name}</b>
Время: <b>{start_datetime}</b>
'''
                    data_master = {
                        'chat_id': master.name.tg_id,
                        'parse_mode': 'HTML',
                        'text': text}
                    requests.post(URL, data=data_master)

                data_client = {
                    'chat_id': client.tg_id,
                    'text': 'Ваша запись успешно выполнена. Вы можете найти все свои записи в разделе "Мои записи"'}
            requests.post(URL, data=data_client)
            return Response({'response': 'ok'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            logger.info(e)
            return Response({'response': False}, status=status.HTTP_400_BAD_REQUEST)

# class APICreateRecords(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         '''Создать запись(и) в журнале'''
#         logger.info('Create records')
#         try:
#             URL = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
#             client_id: int = request.data.get('client_id')
#             client = md.Client.objects.get(id=client_id)

#             # сбор данных для уведомления мастеров и админов
#             masters_data = []
#             masters = request.data.get('masters')
#             for master_item in masters:
#                 master_id: int = master_item.get('master_id')
#                 service_id: int = master_item.get('service_id')
#                 timestamp: str = master_item.get('timestamp')

#                 master = md.Master.objects.get(id=master_id)
#                 service = md.Service.objects.get(id=service_id)
#                 service_date = dt.strptime(timestamp, '%Y-%m-%d %H:%M')

#                 entry, was_create = md.VisitJournal.objects.get_or_create(
#                     visit_client=client,
#                     visit_master=master,
#                     visit_service=service,
#                     date=service_date,
#                 )

#                 logger.info(was_create)
#                 if was_create:
#                     logger.info(entry.id)
#                     logger.info(entry)
#                     if len(masters_data) > 0:
#                         is_exists = False
#                         for data in masters_data:
#                             if data['master_tg_id'] == master.name.tg_id:
#                                 data['services'].append(service.name)
#                                 data['timestamps'].append(timestamp)
#                                 data['entries'].append(entry)
#                                 is_exists = True
#                                 break
#                         if not is_exists:
#                             masters_data.append({
#                                 'master_tg_id': master.name.tg_id,
#                                 'master_name': master.name.name,
#                                 'services': [service.name],
#                                 'timestamps': [timestamp],
#                                 'entries': [entry]
#                             })
#                     else:
#                         masters_data.append({
#                             'master_tg_id': master.name.tg_id,
#                             'master_name': master.name.name,
#                             'services': [service.name],
#                             'timestamps': [timestamp],
#                             'entries': [entry]
#                         })
#             title = f'📝<b>Новая запись!</b>\nКлиент: <b>{client.name}</b>\n'
#             admin_text = title
#             for master_data_item in masters_data:
#                 master_tg_id = master_data_item.get('master_tg_id')
#                 master_name = master_data_item.get('master_name')
#                 data_services = master_data_item.get('services')
#                 data_timestamps = master_data_item.get('timestamps')
#                 data_entries = master_data_item.get('entries')
#                 master_text = title
#                 admin_text += f'\n\n🟢<b>Мастер: {master_name}</b>'
#                 for i, service_item in enumerate(data_services):
#                     data_timestamp = data_timestamps[i]
#                     data_entry = data_entries[i]
#                     text = f'''
#     Услуга: <b>{service_item}</b>
#     Время: <b>{data_timestamp}</b>
#     '''
#                     master_text += text
#                     admin_text += f'''
#     {text}<a href="{BASE_URL}admin/inwork/visitjournal/{data_entry.id}/change/">Запись в журнале</a>'''

#                 # отправляем уведомление об успешной записи мастеру
#                 data_master = {
#                     'chat_id': master_tg_id,
#                     'parse_mode': 'HTML',
#                     'text': master_text}
#                 requests.post(URL, data=data_master)
#             # if client.id == 337:
#             #     logger.info('Админам')
#             #     logger.info(admin_text)
#             #     return Response({'responce': True}, status=status.HTTP_200_OK)
#             # отправляем уведомление об успешной записи клиенту
#             data_client = {
#                 'chat_id': client.tg_id,
#                 'text': 'Ваша запись успешно выполнена. Вы можете найти все свои записи в разделе "Мои записи"'}
#             requests.post(URL, data=data_client)

#             # отправляем уведомление в чат админов
#             if client.tg_id:
#                 admin_text += f'\n\nТелефон клиента: {client.phone}'
#                 finish_services = md.VisitJournal.objects.filter(
#                     visit_client=client, finish=True).count()
#                 if finish_services < 1:
#                     admin_text += '\nКлиент записан в первый раз.'
#                 data = {
#                     'chat_id': CHAT_ADMINS,
#                     'parse_mode': 'HTML',
#                     'text': admin_text}
#                 requests.post(URL, data=data)
#             return Response({'responce': True}, status=status.HTTP_200_OK)
#         except Exception as e:
#             logger.info(e)
#             return Response({'responce': False}, status=status.HTTP_400_BAD_REQUEST)


# Для админки
class APIMonthMastersShedule(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Получить имена и id мастеров и их рабочие дни на выбранный месяц'''
        month: str = request.data.get('month')
        year: str = request.data.get('year')
        masters = md.Master.objects.all()
        masters_schedules: list = []
        for master in masters:
            schedule = md.MasterSchedule.objects.filter(
                master=master,
                date__month=month,
                date__year=year,
            ).values('date')
            masters_schedules.append(
                {
                    'id': master.id,
                    'name': master.name.name.split(' - ')[0],
                    'schedule': list(schedule),
                }
            )
        return Response({'schedule': masters_schedules}, status=status.HTTP_200_OK)


class APICreateSchedule(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Создать записи графика мастеров'''
        new_schedules: list = request.data.get('new_schedules')
        selected_month: str = request.data.get('selectedMonth')

        for schedule in new_schedules:
            # создаём новые записи
            master = md.Master.objects.get(id=schedule.get('masterID'))
            work_dates = schedule.get('workDates')
            dates: list = [dt.strptime(date, '%Y-%m-%d')
                           for date in work_dates]
            for selected_date in dates:
                existing_schedule = md.MasterSchedule.objects.filter(
                    master=master, date=selected_date).first()

                start_time = existing_schedule.start_time if existing_schedule and existing_schedule.start_time else START_WORK_TIME_DEFAULT
                end_time = existing_schedule.end_time if existing_schedule and existing_schedule.end_time else END_WORK_TIME_DEFAULT

                md.MasterSchedule.objects.update_or_create(
                    master=master,
                    date=selected_date,
                    defaults={'start_time': start_time, 'end_time': end_time}
                )

            # очистка убранных записей
            schedule_entries = md.MasterSchedule.objects.filter(
                master=master).exclude(date__in=dates)
            entries_for_delete = []
            for entry in schedule_entries:
                if entry.date.month == int(selected_month):
                    entries_for_delete.append(entry)
            if entries_for_delete:
                for entry in entries_for_delete:
                    entry.delete()

        return Response({'status': True}, status=status.HTTP_200_OK)


class APIGetMasterWorkTime(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Получить время работы мастера'''
        master_id: int = request.data.get('master_id')
        work_day_date: str = request.data.get('work_day_date')
        work_day_date_start = dt.strptime(work_day_date, '%Y-%m-%d')
        work_day_date_end = work_day_date_start + td(days=1)
        work_day_date = dt.strptime(work_day_date, '%Y-%m-%d').date()

        master = md.Master.objects.get(id=master_id)
        master_schedule = md.MasterSchedule.objects.filter(
            master=master,
            date=work_day_date).values('start_time', 'end_time').first()
        visit_journal_entries = md.VisitJournal.objects.filter(
            visit_master=master,
            date__gte=work_day_date_start,
            date__lt=work_day_date_end,
            finish=False,
            cancel=False
        ).all()

        # создаём список занятого времени
        busy_times = []
        for entry in visit_journal_entries:
            services_duration = entry.visit_service.duration
            entry_time = entry.date
            busy_times.append(entry_time.strftime('%H:%M'))
            while services_duration != 30:
                entry_time += td(minutes=30)
                services_duration -= 30
                busy_times.append(entry_time.strftime('%H:%M'))

        # создаём список всего времени
        work_time = []
        times_count = td(hours=master_schedule.get('start_time').hour)
        while times_count != td(hours=master_schedule.get('end_time').hour):
            str_time = (dt.min + times_count).time().strftime('%H:%M')
            if str_time in busy_times:
                work_time.append({
                    'time': str_time,
                    'busy': True
                })
            else:
                work_time.append({
                    'time': str_time,
                    'busy': False
                })
            times_count += td(hours=0.5)
        master_name = str(master.name)
        return Response({
            'work_time': work_time,
            'master_name': master_name
        }, status=status.HTTP_200_OK)


class APIGetDateEventsForAll(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Получение всех событий всех мастеров на выбранную дату'''
        date_string: str = request.data.get('date')
        date: dt = dt.strptime(date_string, '%Y-%m-%d')
        visits = md.VisitJournal.objects.filter(
            date__date=date, cancel=False).order_by('date')
        masters_db = md.Master.objects.all()

        data = {
            'date': date_string,
        }
        masters = []
        weekend_masters = []
        for master in masters_db:
            master_data = get_master_schedule(master, date, visits, admin=True)
            if master_data.get('is_weekend'):
                weekend_masters.append(master_data)
            else:
                masters.append(master_data)
        data['masters'] = masters + weekend_masters
        return Response(data, status=status.HTTP_200_OK)


class APIGetDateEventsForOne(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Получение всех событий всех мастеров на выбранную дату'''
        date_string: str = request.data.get('date')
        master_id: str = request.data.get('master_id')
        date: dt = dt.strptime(date_string, '%Y-%m-%d')
        master_db = md.Master.objects.filter(name__id=master_id).first()
        visits = md.VisitJournal.objects.filter(
            date__date=date, visit_master=master_db, cancel=False).order_by('date')

        master_data = get_master_schedule(master_db, date, visits)
        masters = [master_data]
        data = {
            'date': date_string,
            'masters': masters
        }
        return Response(data, status=status.HTTP_200_OK)


class APILogger(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Логгирование фронта'''
        log_data = request.data.get('log_data')
        logger.info('//////////////////////////////')
        logger.info(log_data)

        return Response({'status': True}, status=status.HTTP_200_OK)
