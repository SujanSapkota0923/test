from rest_framework import permissions


class IsadminOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access certain views.
    """
    def has_permission(self, request, view):
        # SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']
        if request.method in permissions.SAFE_METHODS:
            return True  # anyone can view
        return request.user and request.user.is_staff  # only admin can edit
    
