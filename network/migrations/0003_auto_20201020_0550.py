# Generated by Django 3.1.1 on 2020-10-20 05:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_auto_20201020_0550'),
        ('network', '0002_auto_20201017_0824'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['created_at'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='vpc',
            name='deleted_version',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='vpc',
            name='cidr',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='vpc',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterUniqueTogether(
            name='vpc',
            unique_together={('account', 'identity', 'deleted_version'), ('cidr', 'deleted_version'), ('name', 'deleted_version')},
        ),
        migrations.CreateModel(
            name='DataDisk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network.instance')),
            ],
            options={
                'ordering': ['created_at'],
                'abstract': False,
            },
        ),
    ]
