from django.db import models
from apps.users.models import CustomUser
from django.utils import timezone
from datetime import timedelta


def dtime():
    return timezone.now() + timedelta(hours=3)

# Custom answer sheets model
class CustomSheet(models.Model):
    id = models.AutoField(primary_key=True)
    regdate = models.DateTimeField(default=dtime)
    names = models.CharField(max_length=200)
    teacher = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='teacher')
    published = models.BooleanField(default=False)
    objects = models.Manager()
    
    def __str__(self):
        return str(self.names)
    

# HeaderBoxes model
class HeaderBoxes(models.Model):
    id = models.AutoField(primary_key=True)
    regdate = models.DateTimeField(default=dtime)
    contents = models.JSONField(null=True, default=None)
    sheet = models.ForeignKey(CustomSheet, on_delete=models.PROTECT, related_name='sheet_header')
    objects = models.Manager()
    
    def __str__(self):
        return str(self.contents)
    

# Questions model
class Questions(models.Model):
    id = models.AutoField(primary_key=True)
    regdate = models.DateTimeField(default=dtime)
    qn_type = models.CharField(null=True, default=None, max_length=200)
    qn_number = models.IntegerField(null=True, default=None)
    show_labels = models.BooleanField(null=True, default=True)
    questions = models.JSONField(null=True, default=None)
    sheet = models.ForeignKey(CustomSheet, on_delete=models.PROTECT, related_name='sheet_questions')
    objects = models.Manager()
    
    def __str__(self):
        return str(self.questions)
