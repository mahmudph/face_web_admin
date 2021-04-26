from django.http import JsonResponse
from face_recognation.models import Transaction
from django.views.generic import ListView
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
import urllib.request
import numpy as np
import json
import cv2
import os


base_path= os.path.abspath(os.path.dirname(__name__))

FACE_DETECTOR_PATH = base_path + "/face_recognation/opencv-files/haarcascade_frontalface_default.xml"

FACE_TRAINER_MODEL = base_path + "/output/trainer.yaml"

@method_decorator(csrf_exempt, name='dispatch')
class FaceRecognation(ListView):
    model = Transaction
    
    def predict(self, image):
        subjects = ["", "Agus", "Andy", "Beni", 'Deriman', "Jepa", "Nando", "Oriza", "Peri", "Roby", 'Sandiago']

        img = image.copy()
        
        face, rect = self.detect_face(image)

        #predict the image using our face recognizer 
        face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        face_recognizer.load(FACE_TRAINER_MODEL)

        label, confidence = face_recognizer.predict(face)
        
        label_text = subjects[label]
        
        draw_rectangle(img, rect)
        
        draw_text(img, label_text, rect[0], rect[1]-5)
        return img, label_text
        # return None, None


    def detect_face(self, img):

        print(img)
        WIDTH_IMAGE = 300
        HEIGHT_IMAGE=400
        ob = cv2.resize(img, (WIDTH_IMAGE,HEIGHT_IMAGE)) # 1
        gray = cv2.cvtColor(ob, cv2.COLOR_BGR2GRAY)
        
        face_cascade = cv2.CascadeClassifier(FACE_DETECTOR_PATH)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5);
        
        if (len(faces) == 0):
            return None, None
        
        (x, y, w, h) = faces[0]
        
        return gray[y:y+w, x:x+h], faces[0]

    def post(self, request, *args, **kwargs):

        data = {"success": False}

        if request.method == "POST":
            if request.FILES.get("image", None) is not None:
                image = self.grab_image(stream=request.FILES["image"])
            else:
                url = request.POST.get("url", None)

                if url is None:
                    data["error"] = "No URL provided."
                    return JsonResponse(data)

                image = self.grab_image(url=url)

            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            image,label = self.predict(image)
            data['label'] = label
            data["success"] = True

        return JsonResponse(data)


    def grab_image(self,path=None, stream=None, url=None):

        if path is not None:
            image = cv2.imread(path)

        else:	
            if url is not None:
                resp = urllib.urlopen(url)
                data = resp.read()

            elif stream is not None:
                data = stream.read()
            
            image = np.asarray(bytearray(data), dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image