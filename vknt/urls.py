from django.contrib import admin
from django.views.generic import TemplateView
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
  path("robots.txt", TemplateView.as_view(
        template_name="robots.txt",
        content_type="text/plain"
    )),
  path('', include('location.urls')),
  path('json/', include('cmnsd.urls')),
  path('admin/', admin.site.urls),
  path('', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)