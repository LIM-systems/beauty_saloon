# Generated by Django 4.2.7 on 2023-11-15 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inwork', '0003_alter_category_services'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='services',
            field=models.ManyToManyField(blank=True, to='inwork.service', verbose_name='Услуги'),
        ),
    ]
