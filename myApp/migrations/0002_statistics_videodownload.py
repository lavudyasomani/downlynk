# Generated by Django 5.1.7 on 2025-04-01 19:07

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visits', models.IntegerField(default=0)),
                ('image_downloads', models.IntegerField(default=0)),
                ('video_downloads', models.IntegerField(default=0)),
                ('movie_downloads', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='VideoDownload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('url', models.URLField()),
                ('file_path', models.FileField(upload_to='videos/')),
                ('downloaded_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
