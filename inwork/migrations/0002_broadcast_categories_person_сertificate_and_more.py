# Generated by Django 4.2.7 on 2024-08-14 14:18

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inwork', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255,
                 verbose_name='Название сертификата')),
                ('description', models.TextField(verbose_name='Описание')),
                ('price', models.IntegerField(
                    help_text='Введите цену сертификата в рублях', verbose_name='Цена')),
            ],
            options={
                'verbose_name': 'Сертификат',
                'verbose_name_plural': 'Сертификаты',
            },
        ),
    ]
