# Generated by Django 3.2.6 on 2021-09-21 11:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0020_alter_issue_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issue',
            options={'ordering': ('-creation_date',), 'verbose_name': 'Issue', 'verbose_name_plural': 'Issues'},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ('-creation_date',), 'permissions': [('change_project_issue', 'Can edit issues linked to this project')]},
        ),
    ]
