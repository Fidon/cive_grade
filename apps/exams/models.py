from django.db import models
from apps.users.models import CustomUser
from apps.answer_sheets.models import CustomSheet
from apps.students.models import Students
from django.utils import timezone
from datetime import timedelta


def dtime():
    return timezone.now() + timedelta(hours=3)

# Exam model
class Exams(models.Model):
    id = models.AutoField(primary_key=True)
    regdate = models.DateTimeField(default=dtime)
    names = models.CharField(max_length=200)
    answersheet = models.ForeignKey(CustomSheet, on_delete=models.PROTECT, related_name='exam_sheet')
    teacher = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='exam_teacher')
    describe = models.TextField(null=True, default=None)
    lastEdited = models.DateTimeField(null=True, default=None)
    deleted = models.BooleanField(default=False)
    objects = models.Manager()
    
    def __str__(self):
        return str(self.names)
    

# Results model
class Results(models.Model):
    id = models.AutoField(primary_key=True)
    regdate = models.DateTimeField(default=dtime)
    exam = models.ForeignKey(Exams, on_delete=models.PROTECT, related_name='res_exam')
    student = models.ForeignKey(Students, on_delete=models.PROTECT, related_name='res_student', null=True, default=None)
    regnumber = models.CharField(max_length=200, null=True, default=None)
    marks = models.FloatField()
    total = models.FloatField()
    objects = models.Manager()
    
    def __str__(self):
        return str(self.id)
