# DJANGO REST FRAMEWORK (DRF) API VIEW 
# Main Purpose: To define an API endpoint (UserProfileView) that allows
# a client (like a web or mobile app) to **fetch the profile data of the currently
# authenticated user**. It acts as a secure data gateway, ensuring only logged-in
# users can retrieve their own information.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import User


class UserProfileView(APIView):
    """
    Basic user profile view
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
        })