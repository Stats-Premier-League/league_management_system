# DJANGO ROOT URL CONFIGURATION (Often config/urls.py or project_name/urls.py)
# Main Purpose: This file is the master router for the entire Django project.
# Its primary role is to map incoming URLs (web addresses) to the appropriate
# Django view functions or to delegate the routing to smaller, application-specific
# URL files (like apps.core.urls). It also handles serving non-code files
# (media and debug assets) exclusively during development.

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.core.urls')),
]

# Server medial files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URLS, document_root=settings.MEDIA_ROOT)

    # Debug toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass    