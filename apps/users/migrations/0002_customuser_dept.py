# Generated by Django 5.0.3 on 2024-06-10 03:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='dept',
            field=models.IntegerField(default=2),
        ),
    ]
