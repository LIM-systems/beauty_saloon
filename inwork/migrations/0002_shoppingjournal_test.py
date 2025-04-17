from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('inwork', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingjournal',
            name='test',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='shoppingjournal',
            name='cert_uid',
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
