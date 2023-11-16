from django.contrib import admin
import inwork.models as md


@admin.register(md.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'telegram_id')
    list_filter = ('name', 'phone', 'telegram_id')
    readonly_fields = ('telegram_id',)


@admin.register(md.Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate', 'telegram_id')
    list_filter = ('name', 'rate', 'telegram_id')
    readonly_fields = ('telegram_id',)


@admin.register(md.Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'price')
    list_filter = ('name', 'duration', 'price')


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
    list_display = ('visit_client', 'visit_master', 'date', 'visit_service')
    list_filter = ('visit_client', 'visit_master', 'date', 'visit_service')