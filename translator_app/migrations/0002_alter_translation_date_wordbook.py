# Generated by Django 4.1.7 on 2023-04-10 16:37

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('translator_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 10, 16, 37, 7, 108461, tzinfo=datetime.timezone.utc)),
        ),
        migrations.CreateModel(
            name='Wordbook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.CharField(default='Нет названия', max_length=100)),
                ('phrase', models.TextField(max_length=200)),
                ('translated', models.TextField(max_length=400)),
                ('date', models.DateTimeField(default=datetime.datetime(2023, 4, 10, 16, 37, 7, 109461, tzinfo=datetime.timezone.utc))),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
