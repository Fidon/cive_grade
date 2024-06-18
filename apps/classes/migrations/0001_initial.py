# Generated by Django 5.0.3 on 2024-06-14 09:41

import apps.classes.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Student_class',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('regdate', models.DateTimeField(default=apps.classes.models.dtime)),
                ('names', models.CharField(max_length=200)),
                ('abbrev', models.CharField(max_length=200)),
                ('describe', models.TextField(default=None, null=True)),
                ('lastEdited', models.DateTimeField(default=None, null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='class_teacher', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
