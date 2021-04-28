from django.http import JsonResponse,HttpResponseNotFound
from face_recognation.models import Transaction, UserTarget
from django.views.generic import ListView
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.conf import settings # new
from datetime import datetime
import urllib.request
import numpy as np
import json
import cv2
import os


base_path= os.path.abspath(os.path.dirname(__name__))

FACE_DETECTOR_PATH = base_path + "/face_recognation/opencv-files/lbpcascade_frontalface.xml"
FACE_TRAINER_MODEL = base_path + "/face_recognation/output/trainer.yaml"
subjects = ["", "Agus", "Andy kurniawan", "Beni", 'Deriman', "Jepa", "Nando", "Oriza", "Peri", "Roby", 'Sandiago']

@method_decorator(csrf_exempt, name='dispatch')
class FaceRecognation(ListView):
    model = Transaction
    accuracy = []
    image_crop_path = []
    image_recog_path = ""
    pathUploadImage = ""

    
    def predict(self, image):

        img = image.copy()
        
        #predict the image using our face recognizer 
        face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        face_recognizer.read(FACE_TRAINER_MODEL)

        face, rect = self.detect_face(image)

        if(len(face) == 0):
            raise Exception("gambar wajah tidak dikenali")

        label_text = []
        for index, faceItem in enumerate(face):
            label, confidence = face_recognizer.predict(faceItem)
            
            self.accuracy.append(round(100 - confidence))

            label_tem = subjects[label]
            label_text.append(label_tem)
        
            self.draw_rectangle(img, rect[index])

            self.draw_text(img, label_tem, round(100 - confidence), rect[index][0], rect[index][1]-5)   

            imagepath = "face_recognation/{}.png".format(datetime.now().timestamp())
        
            dirImage = os.path.join(settings.MEDIA_ROOT, imagepath)
            
            self.image_recog_path = os.path.join(settings.BASE_URL, "media/{}".format(imagepath))

            cv2.imwrite(dirImage, img)

        return img, label_text

    def draw_rectangle(self,img, rect):
        (x, y, w, h) = rect
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    def draw_text(self,img, text,accuracy, x, y):
        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
        cv2.putText(img, str(accuracy) + " %", (x + 20,y + 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0),2)

    def crop_face(self, faces, image) :
        face_crop = []
        face_img_path = []
        for f in faces:
            x, y, w, h = [ v for v in f ]
            cv2.rectangle(image, (x,y), (x+w, y+h), (0,0,0), 3)
            # Define the region of interest in the image  
            face_crop.append(image[y:y+h, x:x+w])   

        for face in face_crop:

            imagepath = "face_crop/{}.png".format(datetime.now().timestamp())
            dirImage = os.path.join(settings.MEDIA_ROOT, imagepath)

            self.image_crop_path.append(os.path.join(settings.BASE_URL, "media/{}".format(imagepath)))

            cv2.imwrite(dirImage, face)
            face_img_path.append(dirImage)
        return face_img_path
        
    def detect_face(self, img):
        face_cascade = cv2.CascadeClassifier(FACE_DETECTOR_PATH)

        imagegrey = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        faces = face_cascade.detectMultiScale(imagegrey, scaleFactor=1.2, minNeighbors=5)
        
        # for save build
        imageFace = self.crop_face(faces, img)

        # detec only one images
        if (len(faces) == 0):
            return None, None
        
        face_temp_image = []
        face_detect_image = []
        for f in faces:
            x, y, w, h = [ v for v in f ]
            face_detect_image.append(imagegrey[y:y+w, x:x+h])   
            face_temp_image.append(f)

        return face_detect_image, face_temp_image

    def post(self, request, *args, **kwargs):

        error_temp = ""
        dataLabel = []
        data = {"success": False}
        try:
            if request.method == "POST":
                if request.FILES.get("image", None) is not None:
                    image = self.grab_image(stream=request.FILES["image"])
                else:
                    url = request.POST.get("url", None)

                    if url is None:
                        data["error"] = "No URL provided."
                        return JsonResponse(data)

                    image = self.grab_image(url=url)

                
                images,label = self.predict(image)

               
                for x, lab in enumerate(label):
                    dataTarget = UserTarget.objects.filter(name=lab).values()

                    dataTemp = list(dataTarget)

                    if len(dataTemp) == 0:
                        error_temp = "data user tidak ditemukan di database" 


                    for user,item in enumerate(dataTemp):
                        item['path_detect'] = self.image_crop_path[x]
                        item['accuracy'] = self.accuracy[x]
                        item['image'] = os.path.join(settings.BASE_URL, 'media/{}'.format(item['image']))
                         # crete history data here 
                        Transaction(
                            user_predicted= item['id'],
                            accuracy= self.accuracy[x],
                            image_request=self.pathUploadImage, 
                            created_at=datetime.now(),
                            image_recog=self.image_recog_path,
                            image_result=self.image_crop_path[x],
                        ).save()

                    dataLabel.append(dataTemp)

                data["success"] = True
                data['status'] = "OK"
                data['message'] = error_temp if len(dataLabel[0]) == 0  else "" 
                data['data'] = dataLabel[0]
                data['path_recog'] = self.image_recog_path
            else:
                return  HttpResponseNotFound("page not found!")
        except Exception as e:
            print(e)
            dataError = error_temp if error_temp != "" else "wajah tidak dikenali"
            data['success'] = False
            data['status'] = "Error bro"
            data['message'] = dataError
        

        return JsonResponse(data, content_type="application/json")


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
            
            pathImage = 'upload/{}.png'.format(datetime.now().timestamp())

            # PATH UPLOAD IMAGE 
            pathSaveImage= os.path.join(settings.MEDIA_ROOT, pathImage)

            # LINK IMAGE 
            self.pathUploadImage = os.path.join(settings.BASE_URL, "media/{}".format(pathImage))
            cv2.imwrite(pathSaveImage, image)
        return image