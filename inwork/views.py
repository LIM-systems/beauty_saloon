from datetime import datetime as dt, timedelta as td

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

import inwork.models as md
from inwork.utils import find_available_time_for_all_days


class APIAllCategories(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Получить все категории с учетом персон'''
        result = {'categories': []}
        persons: list = request.data.get('persons')
        if not persons:
            persons = md.Person.objects.all().values_list('title', flat=True)
        print(persons)
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
        services = md.Service.objects.filter(
            categories__in=categories).values(
                'id', 'name', 'description', 'price', 'duration')
        if not services:
            return Response(
                {'nodata': 'Услуг по выбранным категориям не найдено'},
                status=status.HTTP_204_NO_CONTENT)

        return Response({'services': services}, status=status.HTTP_200_OK)


class APISelectMasters(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''Получить мастеров по выбранным услугам'''
        services = request.data.get('services')
        masters = md.Master.objects.filter(
            services__in=services).distinct().values(
                'id', 'name__name', 'description')
        if not masters:
            return Response(
                {'nodata': 'Мастеров по выбранным услугам не найдено'},
                status=status.HTTP_204_NO_CONTENT)
        services = md.Service.objects.filter(id__in=services)
        services = [service.name for service in services]
        to_json = {
            'masters': {'services': services, 'services_masters': masters}
        }
        return Response(to_json, status=status.HTTP_200_OK)


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
        return Response({'responce': True}, status=status.HTTP_200_OK)
