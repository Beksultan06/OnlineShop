from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from app.settings.models import Settings


@admin.register(Settings)
class SettingsAdmin(TranslationAdmin):
    list_display = ("title_banner", "telegram", "instagram", "whatsapp")
    fieldsets = (
        ("🌍 Основное", {
            "fields": (
                "telegram", "instagram", "whatsapp",
                "image_banner", "image_about1", "image_about2",
            ),
        }),
        ("🇷🇺 Русский", {
            "fields": (
                "title_banner_ru", "description_banner_ru",
                "about_title_ru", "description_about_ru", "end_about_ru",
                "title_catalog_ru", "review_ru", "description_review_ru",
                "text_footer_ru",
            ),
        }),
        ("🇬🇧 English", {
            "fields": (
                "title_banner_en", "description_banner_en",
                "about_title_en", "description_about_en", "end_about_en",
                "title_catalog_en", "review_en", "description_review_en",
                "text_footer_en",
            ),
        }),
    )
