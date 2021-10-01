# Generated by Django 3.2.6 on 2021-09-29 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issue',
            options={'ordering': ('status', '-creation_date')},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ('creation_date',), 'permissions': [('change_project_issue', 'Can edit issues linked to this project')]},
        ),
        migrations.AlterField(
            model_name='issue',
            name='status',
            field=models.CharField(choices=[('1', 'To-do'), ('2', 'In progress'), ('3', 'In review'), ('4', 'Done')], default='to_do', max_length=20),
        ),
    ]