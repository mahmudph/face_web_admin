"""
this would be a model used for face recognaton
"""

from django.db import models


class UserTarget(models.Model) :
    """this is user would be a target of face recognation"""
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    nim = models.CharField(max_length=16)
    jurusan = models.CharField(max_length=50,)
    fakultas = models.CharField(max_length=50, default="ilmu komputer")
    email =  models.CharField(max_length=100, default="anonymouse@gmail.com")
    image = models.ImageField(upload_to="profile/")

class Transaction(models.Model):
    """Transaction model for save data log"""
    id = models.BigAutoField(primary_key=True)
    image_request = models.CharField(max_length=100) # path of image upload 
    image_result = models.CharField(max_length=150) # path of the image detection
    image_recog = models.CharField(max_length=150, default="person.png") # path of the imgea recognation
    user_predicted = models.IntegerField(default=0)
    accuracy = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_created=True)
