# Generated by Django 5.1.2 on 2024-10-28 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_click_movie_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='click',
            name='movie',
        ),
    ]
