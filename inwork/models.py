from django.db import models
from datetime import timedelta

# Create your models here.


class Client(models.Model):
    name = models.CharField(
        max_length=255, verbose_name='Имя', help_text='Введите ФИО клиента')
    phone = models.CharField(max_length=255, verbose_name='Телефон',
                             help_text='Введите телефон в формате 79001112233')
    tg_id = models.BigIntegerField(
        verbose_name='Телеграм ID', null=True, blank=True)
    description = models.TextField(
        verbose_name='Комментарий', null=True, blank=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.name


class Master(models.Model):
    name = models.CharField(max_length=255, verbose_name='ФИО')
    description = models.TextField(verbose_name='Описание')
    rate = models.FloatField(
        default=0, verbose_name='Оценка', null=True, blank=True)
    tg_id = models.BigIntegerField(
        verbose_name='Телеграм ID', null=True, blank=True)

    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'

    def __str__(self):
        return self.name


class Categories(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')

    class Meta:
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название услуги')
    masters = models.ManyToManyField(
        Master, verbose_name='Мастера', blank=True)
    categories = models.ManyToManyField(
        Categories, verbose_name='Категории', blank=True)
    duration = models.IntegerField(
        verbose_name='Длительность выполнения (минут)')
    description = models.TextField(verbose_name='Описание')
    price = models.IntegerField(verbose_name='Цена(рублей)')

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     self.duration = self.duration * 60
    #     super().save(*args, **kwargs)


class MasterSchedule(models.Model):
    '''Расписание мастера'''
    master = models.ForeignKey(
        Master, on_delete=models.CASCADE, verbose_name='Мастер')
    date = models.DateField(verbose_name='Рабочий день')
    start_time = models.TimeField(verbose_name='Начало работы')
    end_time = models.TimeField(verbose_name='Конец работы')

    class Meta:
        verbose_name = 'График работы мастера'
        verbose_name_plural = 'Графики работы мастеров'

    def __str__(self):
        return self.date


class MasterScheduleTime(models.Model):
    master_schedule = models.ForeignKey(
        MasterSchedule, on_delete=models.CASCADE, verbose_name='Рабочий день')
    time = models.TimeField(verbose_name='Время')
    is_free = models.BooleanField(default=True, verbose_name='Свободно')

    class Meta:
        verbose_name = 'Время'
        verbose_name_plural = 'Время'

    def __str__(self):
        return self.time


class VisitJournal(models.Model):
    '''Журнал записи клиентов'''
    visit_client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name='Клиент')
    visit_master = models.ForeignKey(
        Master, on_delete=models.CASCADE, verbose_name='Мастер')
    date = models.DateField(verbose_name='Дата посещения')
    visit_service = models.ForeignKey(
        Service, on_delete=models.CASCADE, verbose_name='Услуга')
    finish = models.BooleanField(default=False, verbose_name='Услуга оказана')
    estimation = models.IntegerField(
        verbose_name='Оценка', null=True, blank=True)

    class Meta:
        verbose_name = 'Журнал посещений'
        verbose_name_plural = 'Журнал посещений'

    def __str__(self):
        return f'{self.visit_client} - {self.date}'
