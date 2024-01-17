from datetime import datetime as dt, timedelta as td, date

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

import inwork.models as md
from inwork.utils import find_available_time_for_all_days
from env import TOKEN, BASE_URL, CHAT_ADMINS
import requests


class APIAllCategories(APIView):
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


class APISelectServices(APIView):
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


class APISelectMasters(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Получить мастеров по выбранным услугам'''
        services = request.data.get('services')
        masters = md.Master.objects.filter(
            services__in=services).distinct().values(
                'id', 'name__name', 'description', 'services')
        if not masters:
            return Response(
                {'nodata': 'Мастеров по выбранным услугам не найдено'},
                status=status.HTTP_204_NO_CONTENT)
        masters_data = {}
        for master in masters:
            id = master['id']
            service = md.Service.objects.filter(
                id=master.get('services')).first()
            service = {'name': service.name, 'id': service.id}
            if id not in masters_data:
                masters_data[id] = {
                    'id': id,
                    'name': master['name__name'],
                    'description': master['description'],
                    'services': [service]
                }
            else:
                masters_data[id]['services'].append(service)

        result_list = list(masters_data.values())
        return Response({'masters': result_list}, status=status.HTTP_200_OK)


class APIGetMasterSchedule(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Получить свободное время для выбранного мастера на ближайшие дни'''
        master_id: int = request.data.get('master_id')
        services_id: list = request.data.get('services')
        response = find_available_time_for_all_days(master_id, services_id)
        return Response(response, status=status.HTTP_200_OK)


class APICreateRecords(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Создать запись(и) в журнале'''
        client_tg_id: int = request.data.get('client_tg_id')
        for master in request.data.get('masters'):
            master_id: int = master.get('master_id')
            timestamp: str = master.get('timestamp')
            services: list = master.get('services')
            service_start = dt.strptime(timestamp, '%Y-%m-%d %H:%M')
            # переменная для продолжительности предыдущей услуги
            duration = 0
            for num, service_id in enumerate(services):
                client = md.Client.objects.get(tg_id=client_tg_id)
                master = md.Master.objects.get(id=master_id)
                service = md.Service.objects.get(id=service_id)
                # для первой записи родное время
                # для остальных + продолжительность предыдущей услуги
                if num > 0:
                    service_start += td(minutes=duration)
                # создаем запись(и) для клиента в журнале
                md.VisitJournal.objects.create(
                    visit_client=client,
                    visit_master=master,
                    visit_service=service,
                    date=service_start,
                )
                # обновляем переменную продолжительности для расчета следующей услуги
                duration = service.duration
        # отправляем уведомление об успешной записи
        URL = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
        data = {'chat_id': client_tg_id,
                'text': 'Ваша запись успешно выполнена. Вы можете найти все свои записи в разделе "Мои записи"'}
        requests.post(URL, data=data)

        # если это первая запись клиенту то
        finish_services = md.VisitJournal.objects.filter(
            visit_client=client, finish=True).count()
        if finish_services < 1:
            data = {
                'chat_id': CHAT_ADMINS,
                'parse_mode': 'HTML',
                'text': f'''
<a href="{BASE_URL}admin/inwork/visitjournal/?visit_client__id__exact={client.id}">
Клиент {client.name} записан в первый раз.
</a>
<b>Позвоните для подтверждения {client.phone}</b>'''}
            requests.post(URL, data=data)
        return Response({'responce': True}, status=status.HTTP_200_OK)


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
                    'name': master.name.name,
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
                md.MasterSchedule.objects.update_or_create(
                    master=master,
                    date=selected_date,
                    defaults={'start_time': '09:00:00', 'end_time': '21:00:00'}
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
