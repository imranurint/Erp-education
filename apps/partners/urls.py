from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PartnerViewSet, UniversityViewSet

router = DefaultRouter()
router.register('partners', PartnerViewSet)
router.register('universities', UniversityViewSet)

urlpatterns = [path('', include(router.urls))]
