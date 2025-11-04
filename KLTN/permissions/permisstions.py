from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Chỉ cho phép người dùng có role là 'admin'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 3
    
class IsUser(BasePermission):
    """
    Chỉ cho phép người dùng có role là 'user'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 1 or request.user.role == 2)
