from rest_framework.permissions import BasePermission
from strings import *
from rest_framework import permissions
from rest_framework.authtoken.models import Token

class TokenAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION')
        print("saafsfsfsdafs\n\n\n")
        if token:
            # Extract the token part (remove "Bearer " prefix)
            token = token.split(' ')[1]
            try:
                token_obj = Token.objects.get(key=token)
                # You can add additional checks here if needed
                return True
            except Token.DoesNotExist:
                pass
        return False
