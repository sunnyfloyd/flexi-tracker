# Generated by Django 3.2.6 on 2021-09-11 09:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0005_auto_20210911_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
