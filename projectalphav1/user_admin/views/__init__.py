# Import views here to make them available
from .auth_views import LoginView, LogoutView, RegisterView, UserDetailsView

__all__ = [
    'LoginView', 'LogoutView', 'RegisterView', 'UserDetailsView',
]
