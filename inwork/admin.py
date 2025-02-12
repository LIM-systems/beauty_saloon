import asyncio
import json
from os.path import join, exists
from datetime import datetime, timedelta
import csv

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.timezone import now

from bot.CRUD.broadcast import start_test_broadcast
from inwork import models as md
from inwork import forms as fm
from saloon.settings import MEDIA_ROOT, MEDIA_URL
import env
from rangefilter.filters import DateRangeFilter
import logging

logger = logging.getLogger('main')


@admin.register(md.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(md.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'name_with_phone', 'gender', 'get_webapp_url', 'tg_id',
        'last_visit', 'is_blocked', 'description')
    list_filter = ('name', 'gender', 'phone', 'tg_id',
                   'last_visit', 'is_blocked')
    readonly_fields = ('last_visit', 'is_blocked')
    actions = ('export_users_broadcasts',)

    @admin.display(description='Имя')
    def name_with_phone(self, obj: md.Client):
        return format_html(f'{obj.name} {obj.phone}')

    @admin.display(description='Телефон')
    def get_webapp_url(self, obj: md.Client):
        url = f'{env.BASE_URL}/sign-up?id={obj.id}&admin=true'
        return format_html(
            '<a href="{}" target="_blank">{}</a>', url, obj.phone)

    @admin.action(description='Выгрузка для рассылок')
    def export_users_broadcasts(self, request, queryset):
        '''Выгрузка клиентов для рассылки'''
        path = join(MEDIA_ROOT, 'broadcasts/start')
        # имя для файла csv
        filename = datetime.now().strftime('%Y%m%d%H%M')
        file_path = f'{path}/{filename}.csv'
        # создаем файл и записываем в него данные
        with open(file_path, 'w') as csvfile:
            writer = csv.writer(csvfile)
            data = []
            for client in queryset:
                if client.tg_id:
                    data.append([client.name, client.tg_id])
            writer.writerows(data)
        # создание шаблона рассылки
        broadcast = md.Broadcast.objects.create(
            name=f'Новая рассылка {filename} c {len(data)} записями',
            text='''
В это поле вставьте текст, можно использовать HTML теги и имя клиента через {name}

{name} - обращение по имени
<b>Жирный</b>
<i>Курсив</i>
<s>Зачёркнутый</s>
<u>подчеркнутый</u>
<code>код</code>
‌<span class="tg-spoiler">Скрытый текст</span>
<a href="leadconverter.ru">Скрытая ссылка</a>''',
            send_datetime=datetime.now() - timedelta(minutes=15),
            filename=filename
        )
        # перенаправление на страницу созданной рассылки
        return HttpResponseRedirect(f'/admin/inwork/broadcast/{broadcast.id}')


@admin.register(md.Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate', 'preview_mini')
    list_filter = ('name',)
    readonly_fields = ('preview', 'rate')

    @admin.display(description='Превью')
    def preview(self, obj):
        '''Превью фото тренера в админке'''
        return mark_safe(
            f'<img src="{obj.photo.url}" style="max-height: 300px;">')

    @admin.display(description='Превью')
    def preview_mini(self, obj):
        '''Превью фото тренера в админке'''
        return mark_safe(
            f'<img src="{obj.photo.url}" style="max-width: 100px;">')


@admin.register(md.Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(md.Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'price')
    list_filter = ('name', 'categories', 'persons', 'duration', 'price')


@admin.register(md.MasterSchedule)
class MasterScheduleAdmin(admin.ModelAdmin):
    list_display = ('master', 'date', 'start_time', 'end_time')
    list_filter = ('master', 'date', 'start_time', 'end_time')
    ordering = ('-date', 'master')


def serialize_value(value):
    """Пытается сериализовать значение в JSON, возвращает строку если не удается."""
    try:
        return json.dumps(value, indent=4)
    except (TypeError, ValueError):
        return str(value)


@admin.register(md.VisitJournal)
class VisitJournalTimeAdmin(admin.ModelAdmin):
    form = fm.VisitJournalForm
    list_display = ('visit_client', 'visit_master', 'date',
                    'estimation', 'confirmation',
                    'finish', 'cancel', 'description')
    list_filter = ('visit_client', 'visit_master', ('date', DateRangeFilter),
                   'estimation', 'confirmation',
                   'finish', 'cancel')
    readonly_fields = ('estimation',)
    ordering = ('-date',)

    def save_model(self, request, obj, form, change):
        """Переопределение метода сохранения для логирования изменений."""
        # Проверяем, создается ли новая запись или обновляется старая
        if change:  # Если объект изменяется (не создается)
            # Получаем оригинальную версию объекта из базы данных для сравнения
            old_obj = self.model.objects.get(pk=obj.pk)
            changes = {}

            # Сравниваем каждое поле, чтобы увидеть, какие поля были изменены
            for field in form.changed_data:
                old_value = getattr(old_obj, field)
                new_value = form.cleaned_data[field]
                changes[field] = {
                    'old_value': old_value,
                    'new_value': new_value
                }

            # Логирование изменений
            log_message = {
                'date': now().strftime('%Y-%m-%d %H:%M:%S'),
                'action': 'update',
                'object': str(obj),
                'changes': changes
            }
            self.log_changes(log_message)

        else:  # Если создается новый объект
            log_message = {
                'date': now().strftime('%Y-%m-%d %H:%M:%S'),
                'action': 'create',
                'object': str(obj),
                'new_values': {field: form.cleaned_data[field] for field in form.cleaned_data}
            }
            self.log_changes(log_message)

    #     # Вызываем оригинальный метод сохранения, чтобы сохранить объект
        super().save_model(request, obj, form, change)

    def log_changes(self, log_message):
        """
        Метод для логирования изменений
        """
        # Преобразуем лог-сообщение в форматируемый JSON или предоставляем читаемое значение
        formatted_message = {}

        for key, value in log_message.items():
            if isinstance(value, dict):
                formatted_message[key] = {
                    k: serialize_value(v) for k, v in value.items()}
            else:
                formatted_message[key] = serialize_value(value)

        log_message_json = json.dumps(formatted_message, indent=4)

        logger.info('логирование админки')
        logger.info(log_message_json)


@admin.register(md.Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ('name', 'send_datetime', 'download_result_csv')
    list_filter = ('name', 'send_datetime')
    list_per_page = 50
    readonly_fields = ('download_start_csv_details', 'download_result_csv')
    exclude = ('filename',)
    change_form_template = 'custom_change_form.html'

    def response_change(self, request, obj: md.Broadcast):
        '''Кастомизация для тестовой отправки'''
        save = super().response_change(request, obj)
        if '_test_broadcast' in request.POST:
            response = request.POST

            admins = []
            tg_id = response.get('_tg_id')
            name = response.get('admins')
            # соберем отклик если кнопки нажаты
            if tg_id:
                admins.append((tg_id, ''))
            if name == 'Анна':
                admins.append((761164436, 'Анна Администратор'))
            elif name == 'Артем':
                admins.append((317898823, 'Артем Земцов'))
            try:  # отправка сообщений выбранным админам
                asyncio.run(start_test_broadcast(obj, admins))
                for id, name in admins:
                    self.message_user(request, f'Тест отправлен {name} {id}')
            except Exception as e:
                self.message_user(
                    request, f'Ошибка при отправке: {e}', level='error')
                return save
        return save

    def response_post_save_change(self, request, obj):
        '''Обработка после сохранения'''
        save = super().response_post_save_change(request, obj)
        if '_test_broadcast' in request.POST:
            # если нажали Тестовая рассылка
            return redirect(request.path)
        return save

    @admin.display(description='Результат')
    def download_result_csv(self, obj: md.Broadcast):
        '''Ссылка для скачивания файла с результатом'''
        path_url = join(MEDIA_URL, 'broadcasts/finish')
        path_csv = join(MEDIA_ROOT, 'broadcasts/finish')
        # имя файла с результатом рассылки csv
        file_path = f'{path_url}/{obj.filename}.csv'
        link_file = f'{path_csv}/{obj.filename}.csv'
        if not exists(link_file):
            # Если файл не существует
            return format_html('<b style="color:red;">Результат еще не сформирован</b>')
        return format_html(f'<a href="{env.BASE_URL}{file_path}"><b>Скачать файл</b></a>')

    @admin.display(description='Выборка клиентов для рассылки')
    def download_start_csv_details(self, obj: md.Broadcast):
        '''Ссылка для скачивания файла с выборкой при открытии объекта'''
        path_url = join(MEDIA_URL, 'broadcasts/start')
        path_csv = join(MEDIA_ROOT, 'broadcasts/start')
        # имя файла с результатом рассылки csv
        file_path = f'{path_url}/{obj.filename}.csv'
        link_file = f'{path_csv}/{obj.filename}.csv'
        if not exists(link_file):
            # Если файл не существует
            return format_html('-')
        with open(link_file) as csvfile:
            reader = csv.reader(csvfile)
            row_count = sum(1 for row in reader)
        link = f'<a href="{env.BASE_URL}{file_path}"><b>Скачать файл с выборкой ({row_count} клиентов)</b></a>'

        return format_html(link)


@admin.register(md.Сertificate)
class СertificateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price')
    list_filter = ('name', 'description', 'price')


@admin.register(md.ShoppingJournal)
class ShoppingJournalAdmin(admin.ModelAdmin):
    list_display = ('client', 'certificate', 'email', 'date_time')
    list_filter = ('client', 'certificate', 'email', 'date_time')
