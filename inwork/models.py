from django.core.validators import RegexValidator, ValidationError
from django.utils.timezone import timedelta
from django.contrib import messages
from django.db import models
from PIL import Image
from inwork.utils import START_WORK_TIME_DEFAULT, END_WORK_TIME_DEFAULT
import uuid


class Person(models.Model):
    title = models.CharField(max_length=12)
    name = models.CharField(max_length=12)

    class Meta:
        verbose_name = 'Персона'
        verbose_name_plural = 'Персона'

    def __str__(self):
        return self.name


class Client(models.Model):
    GENDERS = (('m', 'Мужчина'), ('w', 'Женщина'))
    phone_regex = RegexValidator(
        regex=r'^\+7\d{10}$',
        message='Номер должен быть в формате +79001112233')

    name = models.CharField(
        max_length=255, verbose_name='Имя',
        help_text='Введите ФИО клиента')
    gender = models.CharField(
        max_length=255, verbose_name='Пол',
        choices=GENDERS, null=True, blank=True)
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
        return f'{self.name} - {self.phone}'


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
    image = models.ImageField(upload_to='services/', verbose_name='Картинка услуги',
                              null=True, blank=True)
    price = models.IntegerField(verbose_name='Цена(рублей)')
    persons = models.ManyToManyField(
        to=Person, verbose_name='Персоны',
        help_text='Выберите для кого доступна услуга')

    def save(self, *args, **kwargs):
        '''Редактирование размеров картинки при необходимости'''
        super().save(*args, **kwargs)

        if self.image:
            max_width = 512
            max_height = 512
            img = Image.open(self.image.path)

            # Проверка размеров и изменение, если необходимо
            if img.width > max_width or img.height > max_height:
                new_size = (min(img.width, max_width),
                            min(img.height, max_height))
                img.thumbnail(new_size)
                img.save(self.image.path)

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
    start_time = models.TimeField(
        verbose_name='Начало работы', default=START_WORK_TIME_DEFAULT)
    end_time = models.TimeField(
        verbose_name='Конец работы', default=END_WORK_TIME_DEFAULT)

    class Meta:
        verbose_name = 'График работы мастера'
        verbose_name_plural = 'Графики работы мастеров'

    def __str__(self):
        return f'{self.master} - {self.date}'


class VisitJournal(models.Model):
    '''Журнал записи клиентов'''
    MATH_ACTIONS = (('plus', 'Прибавление'), ('minus', 'Вычитание'))

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
    math_action = models.CharField(
        max_length=255, verbose_name='Действие',
        choices=MATH_ACTIONS, default='plus')
    math_value = models.IntegerField(
        verbose_name='Значение', null=True, blank=True,
        help_text='Значение должно быть кратным 15')

    class Meta:
        verbose_name = 'Журнал посещений'
        verbose_name_plural = 'Журнал посещений'

    def __str__(self):
        return f'{self.visit_client} - {self.date}'


class Broadcast(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название рассылки'
    )
    text = models.TextField(
        verbose_name='Текст сообщения',
        help_text='В тексте можно использовать HTML теги и вставлять имя клиента {name}'
    )
    photo = models.CharField(
        verbose_name='Фото',
        help_text='Ссылка на фото, не обязательный параметр',
        max_length=255,
        blank=True, null=True
    )
    video = models.CharField(
        verbose_name='Видео',
        help_text='Ссылка на видео, не обязательный параметр',
        max_length=3000,
        blank=True, null=True
    )
    send_datetime = models.DateTimeField(
        verbose_name='Когда отправить',
        help_text='Указывайте московское время отправки'
    )
    filename = models.CharField(
        max_length=255,
        verbose_name='Имя файла',
        help_text='Имя файла csv с выборкой клиентов'
    )

    class Meta:
        ordering = ('-send_datetime',)
        verbose_name = 'Ручные рассылки'
        verbose_name_plural = 'Ручные рассылки'

    def __str__(self):
        return f'{self.name}'


class Certificate(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название сертификата'
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    price = models.IntegerField(
        verbose_name='Цена',
        help_text='Введите цену сертификата в рублях',
        unique=True
    )
    image = models.ImageField(upload_to='certificates/', verbose_name='Изображение сертификата',
                              default='certificates/default.png')

    class Meta:
        verbose_name = 'Сертификат'
        verbose_name_plural = 'Сертификаты'

    def __str__(self):
        return f'{self.name}'


class ShoppingJournal(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name='Клиент')
    cert_uid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    client_cert = models.ForeignKey(
        Certificate, on_delete=models.CASCADE, verbose_name='Сертификат')
    email = models.CharField(max_length=255, verbose_name='Email')
    date_time = models.DateTimeField(auto_now_add=True)
    sum = models.IntegerField(verbose_name='Сумма')
    was_used = models.BooleanField(default=False, verbose_name='Использован?')

    class Meta:
        verbose_name = 'Журнал покупок'
        verbose_name_plural = 'Журналы покупок'

    def __str__(self):
        return f'{self.client_cert.name}'
