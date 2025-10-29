from django.urls import path
from django.views.generic import RedirectView
from .views.auth_views import LoginView, LogoutView, RegisterView, UserDetailsView, CSRFTokenView

# URL patterns for user_admin app
urlpatterns = [
    # Temporarily disabled redirect to debug admin issues
    # path('', RedirectView.as_view(url='/admin/', permanent=False)),
    # CSRF token endpoint - must be called before login to get CSRF cookie
    path('api/auth/csrf/', CSRFTokenView.as_view(), name='csrf-token'),
    # Authentication endpoints
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/user/', UserDetailsView.as_view(), name='user-details'),
]
