from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Permission that only allows admin users to access the view
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role == 'admin'
        )


class IsAdminOrManager(BasePermission):
    """
    Permission that allows admin or manager users to access the view
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role in ['admin', 'manager']
        )


class IsStaffUser(BasePermission):
    """
    Permission that allows any staff member (admin, manager, staff, etc.) to access the view
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.is_staff_member()
        )


class IsOwnerOrStaff(BasePermission):
    """
    Permission that allows staff members or the owner of the object to access
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Staff members have full access
        if request.user.is_staff_member():
            return True
        
        # Users can only access their own data
        return obj == request.user or (hasattr(obj, 'user') and obj.user == request.user)


class ReadOnlyPermission(BasePermission):
    """
    Permission that allows read-only access for authenticated users
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.method in permissions.SAFE_METHODS
        )


class RoleBasedPermission(BasePermission):
    """
    Custom permission class that checks permissions based on user role and action
    """
    # Define permission mappings for different actions
    PERMISSION_MAPPING = {
        'admin': {
            'create': True,
            'read': True,
            'update': True,
            'delete': True,
            'manage_users': True,
            'view_reports': True,
            'manage_settings': True,
        },
        'manager': {
            'create': True,
            'read': True,
            'update': True,
            'delete': False,
            'manage_users': False,
            'view_reports': True,
            'manage_settings': False,
        },
        'staff': {
            'create': True,
            'read': True,
            'update': True,
            'delete': False,
            'manage_users': False,
            'view_reports': False,
            'manage_settings': False,
        },
        'customer': {
            'create': False,
            'read': False,  # Only own data
            'update': False,  # Only own data
            'delete': False,
            'manage_users': False,
            'view_reports': False,
            'manage_settings': False,
        },
    }
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Get user role
        user_role = request.user.role
        
        # Map HTTP methods to actions
        method_action_mapping = {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
        }
        
        action = method_action_mapping.get(request.method)
        if not action:
            return False
        
        # Check if user role has permission for this action
        role_permissions = self.PERMISSION_MAPPING.get(user_role, {})
        return role_permissions.get(action, False)
    
    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        
        user_role = request.user.role
        
        # Admin has access to everything
        if user_role == 'admin':
            return True
        
        # Manager and staff have limited object access
        if user_role in ['manager', 'staff']:
            # Allow access to most objects but not critical system data
            return True
        
        # Customers can only access their own data
        if user_role == 'customer':
            return obj == request.user or (hasattr(obj, 'user') and obj.user == request.user)
        
        return False