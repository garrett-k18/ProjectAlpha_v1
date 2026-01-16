from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """
    Extended user profile model to store additional user information
    One-to-one relationship with Django's built-in User model
    """
    # Link to the Django User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Additional fields
    job_title = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # Access level for permissions (0-100, higher means more access)
    access_level = models.IntegerField(default=10)
    
    # User preferences
    theme_preference = models.CharField(max_length=20, default='light')
    notification_enabled = models.BooleanField(default=True)
    
    # Password management
    # Flag to indicate if user must change their password on next login
    # Set to True when admin creates user with temporary password
    must_change_password = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['access_level']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to automatically create a UserProfile when a User is created
    
    Args:
        sender: The model class (User)
        instance: The actual instance being saved
        created: Boolean; True if a new record was created
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created=False, **kwargs):
    """
    Ensure a UserProfile exists and save it whenever a User is saved.
    This handles cases where existing users (created before signals were added)
    don't yet have an associated profile. Login updates last_login and triggers
    post_save on User, so we must not assume instance.profile exists.
    """
    # Create the profile if missing, then save it
    profile, _ = UserProfile.objects.get_or_create(user=instance)
    profile.save()
