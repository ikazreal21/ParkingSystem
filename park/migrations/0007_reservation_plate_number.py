# Generated by Django 4.2.11 on 2025-06-07 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('park', '0006_parked_parking_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='plate_number',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
