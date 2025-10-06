from modeltranslation.translator import TranslationOptions, register

from app.settings.models import Settings

@register(Settings)
class SettingsTranslationOptions(TranslationOptions):
    fields = ("title_banner", "description_banner", 'about_title', 'description_about', 'end_about',
    'title_catalog', 'review', 'description_review', 'text_footer')