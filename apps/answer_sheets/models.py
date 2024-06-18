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
    heading = models.TextField(null=True, default=None)
    circles_count = models.IntegerField(default=0)
    squares_count = models.IntegerField(default=0)
    teacher = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='teacher')
    published = models.BooleanField(default=False)
    objects = models.Manager()
    
    def __str__(self):
        return str(self.names)
    

# Questions model
class Questions(models.Model):
    id = models.AutoField(primary_key=True)
    regdate = models.DateTimeField(default=dtime)
    qn_type = models.CharField(null=True, default=None, max_length=200)
    qn_number = models.IntegerField(null=True, default=None)
    qn_marks = models.FloatField(default=1.0)
    questions = models.JSONField(null=True, default=None)
    sheet = models.ForeignKey(CustomSheet, on_delete=models.PROTECT, related_name='sheet_questions')
    objects = models.Manager()
    
    def __str__(self):
        return str(self.questions)



# Answers model
class Marking_scheme(models.Model):
    id = models.AutoField(primary_key=True)
    regdate = models.DateTimeField(default=dtime)
    qn_number = models.IntegerField()
    qn_type = models.CharField(null=True, default=None, max_length=20)
    qn_options = models.CharField(null=True, default=None, max_length=200)
    qn_indices = models.CharField(max_length=200)
    qn_answer = models.CharField(null=True, default=None, max_length=200)
    sheet = models.ForeignKey(CustomSheet, on_delete=models.PROTECT, related_name='sheet_answers')
    question = models.ForeignKey(Questions, on_delete=models.PROTECT, related_name='question_answers', null=True, default=None)
    objects = models.Manager()
    
    def __str__(self):
        return str(self.qn_options)

