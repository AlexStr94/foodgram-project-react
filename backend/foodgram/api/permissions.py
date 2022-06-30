from rest_framework import permissions


class RecipePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return ((request.method in permissions.SAFE_METHODS)
                or (request.user
                    and request.user.is_authenticated
                    )
                )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return (request.user
                    and request.user.is_authenticated)
        if request.method == 'PATCH' or request.method == 'DELETE':
            return (request.user.is_staff
                    or obj.author == request.user)
        return False
