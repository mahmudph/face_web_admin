from django.contrib import admin
from face_recognation.models import UserTarget, Transaction

# Register your models here.

admin.site.register(Transaction)
admin.site.register(UserTarget)