# Generated by Django 5.0.3 on 2024-06-02 11:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0002_exams_describe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exams',
            old_name='published',
            new_name='deleted',
        ),
    ]
