from rest_framework import serializers
from django.contrib.auth.models import User
from ..models.user_profile import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model
    Handles conversion between UserProfile instances and Python primitives
    """
    class Meta:
        model = UserProfile
        fields = [
            'job_title', 'department', 'phone_number', 'profile_picture',
            'access_level', 'theme_preference', 'notification_enabled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model
    Handles conversion between User instances and Python primitives
    Includes nested UserProfile data
    """
    # Nested serializer for profile data
    profile = UserProfileSerializer(read_only=True)
    
    # Password field is write-only (won't be included in responses)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'date_joined',
            'last_login', 'password', 'profile'
        ]
        read_only_fields = ['id', 'is_active', 'is_staff', 'is_superuser', 
                           'date_joined', 'last_login']
    
    def create(self, validated_data):
        """
        Override create method to handle password hashing
        
        Args:
            validated_data: Dictionary of validated data from request
            
        Returns:
            User: Created user instance
        """
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user
    
    def update(self, instance, validated_data):
        """
        Override update method to handle password updates
        
        Args:
            instance: User instance to update
            validated_data: Dictionary of validated data from request
            
        Returns:
            User: Updated user instance
        """
        password = validated_data.pop('password', None)
        
        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Handle password separately for proper hashing
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance
