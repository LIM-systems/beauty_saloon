# Generated by Django 4.2.7 on 2023-12-21 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inwork', '0022_visitjournal_confirmation_alter_service_categories_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitjournal',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Комментарий'),
        ),
    ]
