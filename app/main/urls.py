from django.urls import path, include
from rest_framework import routers

from . import views
    
router = routers.DefaultRouter()
router.register('drone', views.DroneViewset)
router.register('medication', views.MedicationViewset)

urlpatterns = [
    path('', include(router.urls)),
]
