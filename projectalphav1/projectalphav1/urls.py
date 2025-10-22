"""
URL configuration for projectalphav1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/acq/', include('acq_module.urls')),
    path('api/', include('am_module.urls')),
    path('api/core/', include('core.urls')),  # Core module API endpoints (assumptions, etc.)
    # Include user_admin URLs directly (they already have the /api/auth/ prefix)
    path('', include('user_admin.urls')),
    # WHAT: Ensure favicon requests serve the static asset instead of hitting the SPA catch-all.
    # WHY: Without this redirect, /favicon.ico matches the catch-all and triggers TemplateDoesNotExist.
    # HOW: Redirect to the collected static favicon served by WhiteNoise/Django.
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico', permanent=True)),
]

# Serve Vue SPA for non-API routes in development and production
# This catch-all pattern must be last to avoid conflicting with API routes
# Exclude /static/ and /media/ so WhiteNoise can serve them
urlpatterns.append(
    re_path(r'^(?!api/|static/|media/).*$', TemplateView.as_view(template_name='index.html'))
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
