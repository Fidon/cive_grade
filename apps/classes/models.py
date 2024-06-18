from django.db import models
from apps.users.models import CustomUser
from django.utils import timezone
from datetime import timedelta


def dtime():
    return timezone.now() + timedelta(hours=3)

# Student class model
class Student_class(models.Model):
    id = models.AutoField(primary_key=True)
    regdate = models.DateTimeField(default=dtime)
    names = models.CharField(max_length=200)
    abbrev = models.CharField(max_length=200)
    duration = models.IntegerField(null=True, default=None)
    teacher = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='class_teacher')
    describe = models.TextField(null=True, default=None)
    lastEdited = models.DateTimeField(null=True, default=None)
    deleted = models.BooleanField(default=False)
    objects = models.Manager()
    
    def __str__(self):
        return str(self.names)