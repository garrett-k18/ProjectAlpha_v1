"""
acq_module.views.brokers package

Plain-language overview:
- This folder holds ALL broker-related API endpoints.
- We separate concerns into two modules:
  - internal.py: endpoints for internal/admin UI (require authentication)
  - invites.py: endpoints for public token-based broker flows (loginless)
- Shared database logic lives in acq_module.services.brokers to avoid duplication.

How to choose where to add an endpoint:
- If the endpoint serves the internal web app (staff users), put it in internal.py
- If the endpoint is accessed via a token link by an external broker, put it in invites.py

Docs reviewed:
- DRF Views: https://www.django-rest-framework.org/api-guide/views/
- DRF Permissions: https://www.django-rest-framework.org/api-guide/permissions/
"""

__all__ = [
    # Names are exported from their respective modules for convenience
]
