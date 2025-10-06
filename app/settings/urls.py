from django.urls import path
from rest_framework.routers import DefaultRouter

from app.settings.views import SettingsAPI

router = DefaultRouter()
router.register("settings", SettingsAPI, basename='settings')

urlpatterns = [
    
]

urlpatterns += router.urls
