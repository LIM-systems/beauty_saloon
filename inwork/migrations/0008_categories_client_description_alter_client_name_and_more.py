# Generated by Django 4.2.7 on 2023-11-27 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inwork', '0007_rename_servises_master_services'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Категорию',
                'verbose_name_plural': 'Категории',
            },
        ),
        migrations.AddField(
            model_name='client',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='client',
            name='name',
            field=models.CharField(help_text='Введите ФИО клиента', max_length=255, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='client',
            name='phone',
            field=models.CharField(help_text='Введите телефон в формате 79001112233', max_length=255, verbose_name='Телефон'),
        ),
        migrations.AddField(
            model_name='service',
            name='categories',
            field=models.ManyToManyField(blank=True, to='inwork.categories', verbose_name='Категории'),
        ),
    ]