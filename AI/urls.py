from django.urls import path
from . import views

urlpatterns = [
    path('upload/',views.index, name="index"),
    path('train/',views.train, name="train"),
    path('',views.home, name="")
]
