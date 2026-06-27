from django.views.generic import TemplateView


class HomeView(TemplateView):
    """
    Frontend bosh sahifasi. Barcha real ish (yuklash, status tekshirish)
    JS orqali mavjud DRF API'ga (/api/jobs/) fetch qilinadi.
    """
    template_name = "home.html"