from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    BranchViewSet, UserViewSet, ExchangeRateViewSet,
    SettingViewSet, NotificationViewSet, AuditLogViewSet,AssetCategoryViewSet, AssetViewSet,
    AssetMaintenanceViewSet, AssetAssignmentViewSet,
)

router = DefaultRouter()
router.register('branches', BranchViewSet)
router.register('users', UserViewSet)
router.register('exchange-rates', ExchangeRateViewSet)
router.register('settings', SettingViewSet)
router.register('notifications', NotificationViewSet, basename='notification')
router.register('audit-log', AuditLogViewSet)
router.register('asset-categories', AssetCategoryViewSet)
router.register('assets', AssetViewSet)
router.register('asset-maintenance', AssetMaintenanceViewSet)
router.register('asset-assignments', AssetAssignmentViewSet)

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
