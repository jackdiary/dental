"""
URL configuration for dental recommendation AI project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView
from apps.clinics.health_views import health_check, readiness_check, liveness_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    # Health check endpoints
    path('api/health/', health_check, name='health_check'),
    path('api/ready/', readiness_check, name='readiness_check'),
    path('api/alive/', liveness_check, name='liveness_check'),
    # Favicon and other root-level static files
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    path('favicon.svg', RedirectView.as_as_view(url='/static/favicon.svg', permanent=True)),
]

# Serve static and media files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Debug toolbar (development only)
if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# SPA Fallback
urlpatterns.append(path('', TemplateView.as_view(template_name='index.html')))
