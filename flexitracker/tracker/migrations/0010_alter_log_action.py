# Generated by Django 3.2.6 on 2021-09-11 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0009_auto_20210911_1321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='action',
            field=models.CharField(choices=[('new', 'New'), ('update', 'Update'), ('delete', 'Delete')], max_length=50),
        ),
    ]
