from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            try:
                if obj.hidden == True:
                    return obj.owner == request.user
            except:
                return True
        return obj.owner == request.user