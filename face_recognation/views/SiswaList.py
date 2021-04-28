from django.http import JsonResponse
from face_recognation.models import UserTarget
from django.views.generic import ListView
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
import json
from django.core.serializers import serialize

class Mahasiswa(ListView):

    def get(self, request, *args, **kwargs):
        data = UserTarget.objects.all().values()

        datatambah = {
            'data':  list(data)
        }
        
        dataResponse = json.dumps(datatambah)
        return HttpResponse(dataResponse, content_type="application/json")