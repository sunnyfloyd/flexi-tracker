# Generated by Django 3.2.6 on 2021-09-12 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0014_alter_log_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='removed_object',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]
