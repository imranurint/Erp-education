from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Super Admin'


class IsBranchAdminOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ('Super Admin', 'Branch Admin')


class IsAccountantOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ('Super Admin', 'Branch Admin', 'Accountant')


class IsCollectorOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in (
            'Super Admin', 'Branch Admin', 'Accountant', 'Collector'
        )


class BranchIsolationMixin:
    """Filter querysets by user's branch unless Super Admin."""

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'Super Admin':
            return qs
        if user.branch:
            return qs.filter(branch=user.branch)
        return qs.none()
