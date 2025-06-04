from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """Разрешение только для автора объекта или только для чтения."""
    
    def has_object_permission(self, request, view, obj):
        # Разрешения на чтение для всех
        if request.method in SAFE_METHODS:
            return True
        
        # Разрешения на запись только для автора объекта
        return obj.author == request.user
