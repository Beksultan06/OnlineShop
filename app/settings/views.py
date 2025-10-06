from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework import permissions

from app.settings.models import Settings
from app.settings.serializers import SettingsSerailizer

class SettingsAPI(GenericViewSet,
                    ListModelMixin):
    queryset = Settings.objects.all()
    serializer_class = SettingsSerailizer
    permission_classes = [permissions.AllowAny]