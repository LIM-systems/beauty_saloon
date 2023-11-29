from django.contrib import admin
from django.utils.safestring import mark_safe
import inwork.models as md


@admin.register(md.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'tg_id',)
    list_filter = ('name', 'phone', 'tg_id')
    # readonly_fields = ('tg_id',)


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
    list_filter = ('name', 'duration', 'masters', 'price')


@admin.register(md.MasterSchedule)
class MasterScheduleAdmin(admin.ModelAdmin):
    list_display = ('master', 'date', 'start_time', 'end_time')
    list_filter = ('master', 'date', 'start_time', 'end_time')


@admin.register(md.MasterScheduleTime)
class MasterScheduleTimeAdmin(admin.ModelAdmin):
    list_display = ('master_schedule', 'time', 'is_free')
    list_filter = ('master_schedule', 'time', 'is_free')


@admin.register(md.VisitJournal)
class VisitJournalTimeAdmin(admin.ModelAdmin):
    list_display = ('visit_client', 'visit_master', 'date',
                    'visit_service', 'estimation', 'finish')
    list_filter = ('visit_client', 'visit_master', 'date',
                   'visit_service', 'estimation', 'finish')
    readonly_fields = ('estimation', 'finish')
