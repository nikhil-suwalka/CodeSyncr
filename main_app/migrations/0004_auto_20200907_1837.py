# Generated by Django 3.1.1 on 2020-09-07 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_file_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='last_changed',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
