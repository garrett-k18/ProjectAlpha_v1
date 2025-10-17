"""Dev-only CSRF bypass middleware (module located in project-level package)."""

# WHAT: Provides a Django middleware that disables CSRF validation while DEBUG=True.
# WHY: Vue development server issues cross-origin POSTs that otherwise fail without CSRF tokens.
# WHERE: Lives inside `projectalphav1/projectalphav1/middleware/` to align with other project-level config.
# HOW: Toggles documented attribute `request._dont_enforce_csrf_checks` before CsrfViewMiddleware executes.

from typing import Callable  # WHAT: Type hint describing the signature of downstream middleware callbacks
from django.conf import settings  # WHAT: Access project settings to inspect the DEBUG flag each request
from django.http import HttpRequest, HttpResponse  # WHAT: Explicit request/response typing for clarity during review


class DevCSRFBuypassMiddleware:
    """Disable CSRF checks when `settings.DEBUG` evaluates to True."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        # WHAT: Store the next callable in the Django middleware chain so we can delegate after we mutate the request.
        # WHY: Django middleware contract supplies `get_response` to enable per-request processing.
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # WHAT: Inspect the DEBUG flag on every request to guarantee prod environments retain CSRF enforcement.
        if settings.DEBUG:
            # WHAT: Flip Django's internal `_dont_enforce_csrf_checks` flag so CsrfViewMiddleware skips validation.
            # WHY: Allows local development POST/PUT/PATCH/DELETE calls from the SPA without needing CSRF cookies.
            request._dont_enforce_csrf_checks = True
        # WHAT: Delegate to the remainder of the middleware stack and ultimately return the response object.
        return self.get_response(request)
