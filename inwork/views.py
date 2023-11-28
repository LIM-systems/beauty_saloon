from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import inwork.models as md


class SignUp(APIView):
    permission_classes = [AllowAny]

    # def post(self, request):
    #     category_id = request.data.get('category_id')
    #     category = md.Category.objects.get(id=category_id)
    #     services = md.Service.objects.filter(category=category).first()

    def get(self, request, tg_id):
        services = md.Service.objects.all()
        masters = md.Master.objects.all()
        services_data = []
        masters_data = []
        for service in services:
            services_data.append({
                'id': service.id,
                'name': service.name,
                'duration': service.duration,
                'description': service.description,
                'price': service.price,
            })
        for master in masters:
            services_ids = []
            for master_service in master.services.all():
                services_ids.append(master_service.id)
            masters_data.append({
                'id': master.id,
                'name': master.name,
                'description': master.description,
                'services': services_ids
            })
        return Response(
            {'services': services_data, 'masters': masters_data},
            status=status.HTTP_200_OK)
