from django.urls import path
from .views import process_update

urlpatterns = [
    path('process', process_update),
]
