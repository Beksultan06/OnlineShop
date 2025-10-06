from rest_framework import serializers
from app.settings.models import Settings

class SettingsSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = [ 'id',
            'telegram', 'instagram', 'whatsapp', 
            'title_banner', 'description_banner', 'image_banner',
            'about_title', 'description_about', 'image_about1', 'image_about2',
            'end_about', 'title_catalog', 'review', 'description_review', 'text_footer'
        ]