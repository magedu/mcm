# Generated by Django 3.1.1 on 2020-10-20 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='message',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='method',
            field=models.CharField(default='sync', max_length=128),
        ),
    ]
