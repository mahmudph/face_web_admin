"""
this would be a model used for face recognaton
"""

from django.db import models


class UserTarget(models.Model) :
    """this is user would be a target of face recognation"""
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    nim = models.CharField(max_length=16)
    jurusan = models.CharField(max_length=50)

class Transaction(models.Model):
    """Transaction model for save data log"""
    id = models.BigAutoField(primary_key=True)
    image_request = models.CharField(max_length=100)
    image_result = models.CharField(max_length=100)
    user_target = models.ForeignKey(UserTarget, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_created=True)
