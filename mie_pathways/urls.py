from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView  # Add this import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.core.urls')),
    path('api/v1/', include('apps.academics.urls')),
    path('api/v1/', include('apps.students.urls')),
    path('api/v1/', include('apps.partners.urls')),
    path('api/v1/', include('apps.accounting.urls')),
    path('api/v1/', include('apps.progression.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/hrm/', include('apps.hrm.urls')),

    # API docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  # API schema
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # Swagger UI
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)