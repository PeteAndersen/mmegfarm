from django.urls import path

from .views import *

app_name = 'bestiary'

urlpatterns = [
    path('', UploadCreatureDataView.as_view()),
]
