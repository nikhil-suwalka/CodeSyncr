# Generated by Django 3.1.1 on 2020-09-07 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='last_changed',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
