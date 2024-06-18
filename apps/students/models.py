from django.db import models
from apps.classes.models import Student_class
from django.utils import timezone
from datetime import timedelta


def dtime():
    return timezone.now() + timedelta(hours=3)

# Student model
class Students(models.Model):
    id = models.AutoField(primary_key=True)
    regdate = models.DateTimeField(default=dtime)
    regnumber = models.CharField(max_length=200)
    names = models.CharField(max_length=200)
    program = models.ForeignKey(Student_class, on_delete=models.PROTECT, related_name='student_program')
    year = models.IntegerField(null=True, default=None)
    deleted = models.BooleanField(default=False)
    objects = models.Manager()
    
    def __str__(self):
        return str(self.names)