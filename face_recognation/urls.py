from django.urls import path
from face_recognation.views import FaceRecognationView, homeClassView, SiswaList


urlpatterns = [
    path('', homeClassView.homeView,),

    path('detect_image', FaceRecognationView.FaceRecognation.as_view()),
    path('get_siswa', SiswaList.Mahasiswa.as_view()),
]



