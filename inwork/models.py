from django.db import models
from datetime import timedelta

# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=255, default='newbie', verbose_name='Имя')
    phone = models.CharField(max_length=255, default='89000000000', verbose_name='Телефон')
    telegram_id = models.BigIntegerField(verbose_name='Телеграм ID', null=True, blank=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.name


class Master(models.Model):
    name = models.CharField(max_length=255, verbose_name='ФИО')
    description = models.TextField(verbose_name='Описание')
    services = models.ManyToManyField('Service', verbose_name='Услуги')
    rate = models.FloatField(default=0, verbose_name='Оценка')
    telegram_id = models.BigIntegerField(verbose_name='Телеграм ID', null=True, blank=True)

    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'
    
    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название услуги')
    duration = models.DurationField(verbose_name='Длительность выполнения (минут)')
    description = models.TextField(verbose_name='Описание')
    price = models.IntegerField(verbose_name='Цена(рублей)')

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.duration = self.duration * 60
        super().save(*args, **kwargs)

class MasterSchedule(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE, verbose_name='Мастер')
    date = models.DateField(verbose_name='Рабочий день')
    start_time = models.TimeField(verbose_name='Начало работы')
    end_time = models.TimeField(verbose_name='Конец работы')

    class Meta:
        verbose_name = 'График работы мастера'
        verbose_name_plural = 'Графики работы мастеров'
    
    def __str__(self):
        return self.date


class MasterScheduleTime(models.Model):
    master_schedule = models.ForeignKey(MasterSchedule, on_delete=models.CASCADE, verbose_name='Рабочий день')
    time = models.TimeField(verbose_name='Время')
    is_free = models.BooleanField(default=True, verbose_name='Свободно')

    class Meta:
        verbose_name = 'Время'
        verbose_name_plural = 'Время'
    
    def __str__(self):
        return self.time


class VisitJournal(models.Model):
    visit_client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    visit_master = models.ForeignKey(Master, on_delete=models.CASCADE, verbose_name='Мастер')
    date = models.DateField(verbose_name='Дата посещения')
    visit_service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Оказанная услуга')

    class Meta:
        verbose_name = 'Журнал посещений'
        verbose_name_plural = 'Журналы посещений'

    def __str__(self):
        return self.date
