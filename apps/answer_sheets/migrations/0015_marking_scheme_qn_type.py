# Generated by Django 5.0.3 on 2024-05-28 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('answer_sheets', '0014_marking_scheme_qn_marks'),
    ]

    operations = [
        migrations.AddField(
            model_name='marking_scheme',
            name='qn_type',
            field=models.CharField(default=None, max_length=20, null=True),
        ),
    ]
