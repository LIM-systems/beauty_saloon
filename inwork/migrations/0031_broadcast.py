# Generated by Django 4.2.7 on 2024-02-07 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inwork', '0030_remove_visitjournal_visit_service_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Broadcast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название рассылки')),
                ('text', models.TextField(help_text='В тексте можно использовать HTML теги и вставлять имя клиента {name}', verbose_name='Текст сообщения')),
                ('photo', models.CharField(blank=True, help_text='Ссылка на фото, не обязательный параметр', max_length=255, null=True, verbose_name='Фото')),
                ('video', models.CharField(blank=True, help_text='Ссылка на видео, не обязательный параметр', max_length=3000, null=True, verbose_name='Видео')),
                ('send_datetime', models.DateTimeField(help_text='Указывайте московское время отправки', verbose_name='Когда отправить')),
                ('filename', models.CharField(help_text='Имя файла csv с выборкой клиентов', max_length=255, verbose_name='Имя файла')),
            ],
            options={
                'verbose_name': 'Ручные рассылки',
                'verbose_name_plural': 'Ручные рассылки',
                'ordering': ('-send_datetime',),
            },
        ),
    ]
