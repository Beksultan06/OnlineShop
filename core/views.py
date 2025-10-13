from django.views.generic import TemplateView

class FrontendApp(TemplateView):
    template_name = "index.html"
