"""Dev-only authentication bypass middleware (module located in project-level package)."""

# WHAT: Provides a Django middleware that disables DRF authentication/permission checks while DEBUG=True.
# WHY: Allows local development without requiring auth tokens, similar to CSRF bypass pattern.
# WHERE: Lives inside `projectalphav1/projectalphav1/middleware/` to align with other project-level config.
# HOW: Sets request.skip_auth flag that views can check, or use DevAuthBypassMixin for ViewSets.

from typing import Callable
from django.conf import settings
from django.http import HttpRequest, HttpResponse


class DevAuthBypassMiddleware:
    """Mark requests as auth-exempt when `settings.DEBUG` evaluates to True."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        # WHAT: Store the next callable in the Django middleware chain so we can delegate after we mutate the request.
        # WHY: Django middleware contract supplies `get_response` to enable per-request processing.
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # WHAT: Inspect the DEBUG flag on every request to guarantee prod environments retain auth enforcement.
        if settings.DEBUG:
            # WHAT: Set a custom flag that views can check to bypass auth
            # WHY: Allows local development API calls without authentication tokens
            # HOW: Views check this flag or use DevAuthBypassMixin which checks DEBUG directly
            request._dev_bypass_auth = True
        else:
            request._dev_bypass_auth = False
        
        # WHAT: Delegate to the remainder of the middleware stack and ultimately return the response object.
        return self.get_response(request)

