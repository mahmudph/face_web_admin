from django.urls import path
from face_recognation.views import FaceRecognationView, homeClassView


urlpatterns = [
    path('', homeClassView.homeView,),
    path('detect_image', FaceRecognationView.FaceRecognation.as_view()),
]

