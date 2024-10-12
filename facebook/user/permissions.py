from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET','HEAD','OPTIONS']:  #can read the object only
            return True

        return obj == request.user      # owner of the object