from django.core.validators import RegexValidator
from django.db import models


class Person(models.Model):
    title = models.CharField(max_length=12)
    name = models.CharField(max_length=12)

    class Meta:
        verbose_name = 'Персона'
        verbose_name_plural = 'Персона'

    def __str__(self):
        return self.name


class Client(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+7\d{10}$',
        message='Номер должен быть в формате +79001112233')

    name = models.CharField(
        max_length=255, verbose_name='Имя',
        help_text='Введите ФИО клиента')
    phone = models.CharField(
        validators=[phone_regex],
        max_length=12, verbose_name='Телефон',
        default='+7', help_text='Введите телефон в формате +79001112233')
    tg_id = models.BigIntegerField(
        verbose_name='Телеграм ID', null=True, blank=True)
    last_visit = models.DateTimeField(
        verbose_name='Последнее посещение', blank=True, null=True)
    description = models.TextField(
        verbose_name='Комментарий', null=True, blank=True)
    is_blocked = models.BooleanField(
        verbose_name='Бот заблокирован', null=True, blank=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.name


class Master(models.Model):
    name = models.ForeignKey(
        to=Client, on_delete=models.CASCADE, verbose_name='ФИО')
    description = models.TextField(verbose_name='Описание')
    services = models.ManyToManyField(
        'Service', verbose_name='Услуги', blank=True)
    rate = models.FloatField(
        default=0, verbose_name='Оценка', null=True, blank=True)
    photo = models.ImageField(
        upload_to='masters/',
        verbose_name='Фото мастера',)

    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'

    def __str__(self):
        return self.name.name


class Categories(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')

    class Meta:
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название услуги')
    categories = models.ManyToManyField(
        Categories, verbose_name='Категории',)
    duration = models.IntegerField(
        verbose_name='Длительность выполнения (минут)')
    description = models.TextField(verbose_name='Описание', blank=True)
    price = models.IntegerField(verbose_name='Цена(рублей)')
    persons = models.ManyToManyField(
        to=Person, verbose_name='Персоны',
        help_text='Выберите для кого доступна услуга')

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return self.name


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
        return f'{self.master} - {self.date}'


class VisitJournal(models.Model):
    '''Журнал записи клиентов'''
    visit_client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name='Клиент')
    visit_master = models.ForeignKey(
        Master, on_delete=models.CASCADE, verbose_name='Мастер')
    date = models.DateTimeField(verbose_name='Дата посещения')
    visit_service = models.ForeignKey(
        Service, on_delete=models.CASCADE, verbose_name='Услуга')
    confirmation = models.DateTimeField(
        verbose_name='Подтверждение', blank=True, null=True)
    cancel = models.BooleanField(default=False, verbose_name='Услуга отменена')
    finish = models.BooleanField(default=False, verbose_name='Услуга оказана')
    estimation = models.IntegerField(
        verbose_name='Оценка', null=True, blank=True)
    description = models.TextField(
        verbose_name='Комментарий', blank=True, null=True)

    class Meta:
        verbose_name = 'Журнал посещений'
        verbose_name_plural = 'Журнал посещений'

    def __str__(self):
        return f'{self.visit_client} - {self.date}'
