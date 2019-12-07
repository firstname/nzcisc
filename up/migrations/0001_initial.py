# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Upfile',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('file_name', models.CharField(max_length=30)),
                ('file_path', models.FileField(upload_to='./upload/')),
                ('file_descr', models.TextField(default='there is no description')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('if_anal', models.CharField(max_length=30, default='False')),
                ('anal_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
