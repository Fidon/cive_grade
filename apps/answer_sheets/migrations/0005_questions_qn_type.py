# Generated by Django 5.0.3 on 2024-04-01 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('answer_sheets', '0004_rename_qn_labels_list_questions_questions_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='qn_type',
            field=models.CharField(default=None, max_length=200, null=True),
        ),
    ]
