# Generated by Django 5.0.3 on 2024-05-27 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('answer_sheets', '0010_delete_studentkeys'),
    ]

    operations = [
        migrations.AddField(
            model_name='customsheet',
            name='heading',
            field=models.TextField(default=None, null=True),
        ),
    ]
