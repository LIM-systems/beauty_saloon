# Generated by Django 4.2.7 on 2023-11-30 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inwork', '0015_remove_master_tg_id_visitjournal_cancel_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitjournal',
            name='cancel',
            field=models.BooleanField(default=False, verbose_name='Услуга отменена'),
        ),
    ]
