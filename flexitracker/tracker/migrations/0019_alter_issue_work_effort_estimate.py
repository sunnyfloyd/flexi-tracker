# Generated by Django 3.2.6 on 2021-09-19 12:39

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0018_remove_issue_work_effort_actual'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='work_effort_estimate',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]