from rest_framework import permissions


class IsAdminUserRole(permissions.BasePermission):
    """
    Permission class for ADMIN role users.
    Only users with ADMIN role can access.
    """
    message = "Only administrators can access this resource."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.has_admin_access()
        )


class IsStaffUserRole(permissions.BasePermission):
    """
    Permission class for STAFF role users.
    ADMIN and STAFF can access.
    """
    message = "You need staff access to perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.has_staff_access()
        )


class IsViewerOrReadOnly(permissions.BasePermission):
    """
    Permission class for VIEWER role users.
    All authenticated users can view, but only STAFF+ can modify.
    """
    message = "You don't have permission to modify this resource."
    
    def has_permission(self, request, view):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for STAFF+
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.has_staff_access()
        )