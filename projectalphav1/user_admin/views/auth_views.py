from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from ..models.user_profile import UserProfile
from django.db import transaction

class LoginView(ObtainAuthToken):
    """
    API endpoint for user login
    Returns authentication token and user details on successful login
    """
    def post(self, request, *args, **kwargs):
        # Get email/username and password from request data
        # Ensure they're strings to prevent TypeError during checks
        email_or_username = request.data.get('email') or ''  # Could be email or username
        password = request.data.get('password') or ''

        # Validate required fields early to avoid 500 errors on bad input
        if not email_or_username or not password:
            return Response({
                'error': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to authenticate with the provided value as username first
        user = authenticate(username=email_or_username, password=password)
        
        # If that fails, try to find a user with the provided email and authenticate
        if not user and ('@' in email_or_username):
            try:
                # Look up the user by email
                user_obj = User.objects.get(email=email_or_username)
                # Then authenticate with the username
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        
        if user:
            # Generate or get token
            token, created = Token.objects.get_or_create(user=user)

            # Ensure profile exists (signal should create it, but guard just in case)
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user)

            # Return token and user data
            # Include must_change_password flag to indicate if user needs to change password
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'access_level': profile.access_level,
                'theme_preference': profile.theme_preference,
                'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
                'must_change_password': profile.must_change_password,
            })
        else:
            # Return error for invalid credentials
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    API endpoint for user logout
    Invalidates the user's authentication token
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Delete the user's token to logout
        request.user.auth_token.delete()
        
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """
    API endpoint for user registration
    Creates a new user and returns authentication token
    """
    permission_classes = [permissions.AllowAny]
    
    @transaction.atomic
    def post(self, request):
        # Get user data from request
        username = request.data.get('email')  # Using email as username
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        # Validate required fields
        if not (username and email and password):
            return Response({
                'error': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return Response({
                'error': 'User with this email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # UserProfile is created automatically via signal
        
        # Generate token
        token, created = Token.objects.get_or_create(user=user)
        
        # Return token and user data
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }, status=status.HTTP_201_CREATED)


class UserDetailsView(APIView):
    """
    API endpoint for retrieving and updating user details
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current user details"""
        user = request.user
        profile = UserProfile.objects.get(user=user)
        
        return Response({
            'user_id': user.pk,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'job_title': profile.job_title,
            'department': profile.department,
            'phone_number': profile.phone_number,
            'access_level': profile.access_level,
            'theme_preference': profile.theme_preference,
            'notification_enabled': profile.notification_enabled,
            'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
        })
    
    @transaction.atomic
    def put(self, request):
        """Update user details"""
        user = request.user
        profile = UserProfile.objects.get(user=user)
        
        # Update User model fields
        if 'first_name' in request.data:
            user.first_name = request.data.get('first_name')
        if 'last_name' in request.data:
            user.last_name = request.data.get('last_name')
        if 'email' in request.data:
            user.email = request.data.get('email')
            # Only update username if it's the same as email (our convention)
            if user.username == user.email:
                user.username = request.data.get('email')
        
        # Update UserProfile fields
        if 'job_title' in request.data:
            profile.job_title = request.data.get('job_title')
        if 'department' in request.data:
            profile.department = request.data.get('department')
        if 'phone_number' in request.data:
            profile.phone_number = request.data.get('phone_number')
        if 'theme_preference' in request.data:
            profile.theme_preference = request.data.get('theme_preference')
        if 'notification_enabled' in request.data:
            profile.notification_enabled = request.data.get('notification_enabled')
        
        # Handle profile picture separately if provided
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        # Save changes
        user.save()
        profile.save()
        
        return Response({
            'message': 'User details updated successfully'
        }, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    API endpoint for users to change their password
    Used for initial password change when must_change_password flag is set
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        """
        Change user's password
        
        Args:
            request.data should contain:
                - old_password: Current password (required for verification)
                - new_password: New password to set
                
        Returns:
            Success message and updated must_change_password status
        """
        # Get old and new passwords from request
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        # Validate required fields
        if not old_password or not new_password:
            return Response({
                'error': 'Both old password and new password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate new password length (Django default minimum is usually enforced)
        if len(new_password) < 8:
            return Response({
                'error': 'New password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get current user
        user = request.user
        
        # Verify old password matches
        if not user.check_password(old_password):
            return Response({
                'error': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if new password is same as old password
        if user.check_password(new_password):
            return Response({
                'error': 'New password must be different from current password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password (Django's set_password handles hashing)
        user.set_password(new_password)
        user.save()
        
        # Get user profile and clear must_change_password flag
        profile = UserProfile.objects.get(user=user)
        profile.must_change_password = False
        profile.save()
        
        # Return success response
        return Response({
            'message': 'Password changed successfully',
            'must_change_password': False
        }, status=status.HTTP_200_OK)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenView(APIView):
    """
    API endpoint to get CSRF token
    This ensures the csrftoken cookie is set for subsequent requests
    Docs: https://docs.djangoproject.com/en/5.2/ref/csrf/#ajax
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Returns CSRF token in response body and sets csrftoken cookie
        Frontend should call this endpoint before making authenticated requests
        """
        csrf_token = get_token(request)
        return Response({
            'csrfToken': csrf_token
        }, status=status.HTTP_200_OK)
