from __future__ import annotations

from typing import Any, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Exists, OuterRef
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from am_module.models import AuditLog
from core.models import AssetIdHub
from core.models.model_core_notification import Notification, NotificationRead
from core.serializers.serial_core_notification import ActivityItemSerializer, NotificationSerializer
from core.views.views_co_assumptions import DevAuthBypassMixin


def _resolve_request_user(request: Request) -> Optional[Any]:
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        return user

    if getattr(settings, "DEBUG", False) and getattr(request, "_dev_bypass_auth", False):
        User = get_user_model()
        return User.objects.order_by("id").first()

    return None


def _format_full_address(street: Any, city: Any, state: Any, postal: Any) -> str:
    street_s = (str(street).strip() if street is not None else "").strip()
    city_s = (str(city).strip() if city is not None else "").strip()
    state_s = (str(state).strip() if state is not None else "").strip()
    postal_s = (str(postal).strip() if postal is not None else "").strip()

    parts: list[str] = []
    if street_s:
        parts.append(street_s)
    city_state = ", ".join([p for p in [city_s, state_s] if p])
    if city_state:
        parts.append(city_state)
    if postal_s:
        if parts:
            parts[-1] = f"{parts[-1]} {postal_s}".strip()
        else:
            parts.append(postal_s)
    return ", ".join([p for p in parts if p]).strip()


def _format_currency(value: Any) -> str:
    """Format numeric value as currency with $ and commas."""
    if value is None:
        return "—"
    try:
        num = float(str(value).replace(",", "").replace("$", "").strip())
        if num == int(num):
            return f"${int(num):,}"
        return f"${num:,.2f}"
    except (ValueError, TypeError):
        return str(value)


def _format_date_value(value: Any) -> str:
    """Format date string (YYYY-MM-DD or ISO) to friendly format like Jan 16, 2026."""
    if value is None:
        return "—"
    s = str(value).strip()
    if not s or s.lower() in ("none", "null", ""):
        return "—"
    try:
        from datetime import datetime
        # Try ISO format first
        if "T" in s:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        else:
            dt = datetime.strptime(s[:10], "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")
    except Exception:
        return s


def _is_currency_field(field_name: str) -> bool:
    """Check if field name suggests it's a currency/money field."""
    f = (field_name or "").lower()
    currency_keywords = [
        "price", "cost", "amount", "balance", "value", "fee", "payment",
        "debt", "arrears", "escrow", "charges", "total", "upb", "bid",
    ]
    return any(kw in f for kw in currency_keywords)


def _is_date_field(field_name: str) -> bool:
    """Check if field name suggests it's a date field."""
    f = (field_name or "").lower()
    date_keywords = ["date", "completion", "expire", "maturity", "due"]
    return any(kw in f for kw in date_keywords)


def _coalesce_display(value: Any, field_name: str = "") -> str:
    """Format value based on field type - currency, date, or plain text."""
    if value is None:
        return "—"
    s = str(value).strip()
    if s == "" or s.lower() == "none" or s.lower() == "null":
        return "—"
    
    # Format based on field type
    if _is_currency_field(field_name):
        return _format_currency(value)
    if _is_date_field(field_name):
        return _format_date_value(value)
    
    return s


def _humanize_field_name(field_name: str) -> str:
    f = (field_name or "").strip()
    if not f:
        return "Field"
    f_lower = f.lower()
    if "status" in f_lower:
        return "Status"
    if f_lower == "task_type":
        return "Task Type"
    return f.replace("_", " ").strip().title()


def _build_hub_label_map(hub_ids: set[int]) -> dict[int, tuple[str, str]]:
    hub_label_map: dict[int, tuple[str, str]] = {}
    if not hub_ids:
        return hub_label_map

    hubs = (
        AssetIdHub.objects.filter(id__in=hub_ids)
        .select_related("acq_asset")
        .prefetch_related("servicer_loan_data")
    )
    for hub in hubs:
        servicer_loan_id = (str(getattr(hub, "servicer_id", "") or "").strip())

        addr = ""
        srd = getattr(hub, "acq_asset", None)
        if srd is not None:
            addr = _format_full_address(
                getattr(srd, "street_address", None),
                getattr(srd, "city", None),
                getattr(srd, "state", None),
                getattr(srd, "zip", None),
            )

        if not addr:
            servicer_rows = list(getattr(hub, "servicer_loan_data", []).all())
            if servicer_rows:
                servicer_rows.sort(
                    key=lambda s: (
                        getattr(s, "reporting_year", 0) or 0,
                        getattr(s, "reporting_month", 0) or 0,
                        getattr(s, "as_of_date", "") or "",
                    ),
                    reverse=True,
                )
                latest = servicer_rows[0]
                addr = _format_full_address(
                    getattr(latest, "address", None),
                    getattr(latest, "city", None),
                    getattr(latest, "state", None),
                    getattr(latest, "zip_code", None),
                )

        hub_label_map[int(hub.id)] = (servicer_loan_id, addr)

    return hub_label_map


class NotificationViewSet(DevAuthBypassMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = _resolve_request_user(self.request)

        if user is None:
            return qs.annotate(is_read=models.Value(False, output_field=models.BooleanField()))

        read_exists = NotificationRead.objects.filter(notification_id=OuterRef("pk"), user=user)
        return qs.annotate(is_read=Exists(read_exists))

    @action(detail=False, methods=["get"], url_path="unread")
    def unread(self, request: Request):
        user = _resolve_request_user(request)
        if user is None:
            qs = Notification.objects.none()
            page = self.paginate_queryset(qs)
            if page is not None:
                ser = self.get_serializer(page, many=True)
                return self.get_paginated_response(ser.data)
            return Response([], status=status.HTTP_200_OK)

        read_exists = NotificationRead.objects.filter(notification_id=OuterRef("pk"), user=user)
        qs = Notification.objects.annotate(is_read=Exists(read_exists)).filter(is_read=False)

        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)

        ser = self.get_serializer(qs, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request: Request, pk: str | None = None):
        user = _resolve_request_user(request)
        if user is None:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        notif = self.get_object()
        NotificationRead.objects.get_or_create(notification=notif, user=user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], url_path="clear-all")
    def clear_all(self, request: Request):
        user = _resolve_request_user(request)
        if user is None:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        unread_ids = (
            Notification.objects.exclude(reads__user=user)
            .values_list("id", flat=True)
        )

        rows = [NotificationRead(notification_id=nid, user=user, read_at=timezone.now()) for nid in unread_ids]
        if rows:
            NotificationRead.objects.bulk_create(rows, ignore_conflicts=True)
        return Response({"marked_read": len(rows)}, status=status.HTTP_200_OK)


class ActivityFeedView(DevAuthBypassMixin, APIView):
    def get(self, request: Request):
        user = _resolve_request_user(request)

        limit_raw = request.query_params.get("limit")
        try:
            limit = int(limit_raw) if limit_raw else 50
        except Exception:
            limit = 50
        limit = max(1, min(limit, 200))

        asset_hub_id = request.query_params.get("asset_hub_id")
        source = (request.query_params.get("source") or "").strip().lower()

        items: list[dict[str, Any]] = []

        if source in ("", "notification", "notifications"):
            n_qs = Notification.objects.all()
            if asset_hub_id:
                try:
                    n_qs = n_qs.filter(asset_hub_id=int(asset_hub_id))
                except Exception:
                    n_qs = n_qs.none()

            if user is not None:
                read_exists = NotificationRead.objects.filter(notification_id=OuterRef("pk"), user=user)
                n_qs = n_qs.annotate(is_read=Exists(read_exists))
            else:
                n_qs = n_qs.annotate(is_read=models.Value(False, output_field=models.BooleanField()))

            notif_rows = list(n_qs.order_by("-created_at", "-id")[: limit * 2])
            hub_ids = {int(n.asset_hub_id) for n in notif_rows if getattr(n, "asset_hub_id", None)}
            hub_label_map = _build_hub_label_map(hub_ids)

            for n in notif_rows:
                actor = getattr(n.created_by, "username", None) if getattr(n, "created_by", None) else None

                hub_pk = getattr(n, "asset_hub_id", None)
                servicer_loan_id, addr = ("", "")
                if hub_pk is not None and int(hub_pk) in hub_label_map:
                    servicer_loan_id, addr = hub_label_map[int(hub_pk)]

                if servicer_loan_id and addr:
                    title = f"{servicer_loan_id} - {addr}"
                elif servicer_loan_id:
                    title = servicer_loan_id
                elif addr:
                    title = addr
                else:
                    title = n.title

                items.append(
                    {
                        "id": f"notification:{n.id}",
                        "source": "notification",
                        "created_at": n.created_at,
                        "title": title,
                        "message": n.message or "",
                        "event_type": n.event_type,
                        "asset_hub_id": n.asset_hub_id,
                        "actor": actor,
                        "is_read": getattr(n, "is_read", False),
                    }
                )

        if source in ("", "audit", "auditlog"):
            a_qs = AuditLog.objects.all()
            if asset_hub_id:
                try:
                    a_qs = a_qs.filter(asset_hub_id=int(asset_hub_id))
                except Exception:
                    a_qs = a_qs.none()

            audit_rows = list(a_qs.order_by("-changed_at", "-id")[: limit * 2])
            hub_ids = {a.asset_hub_id for a in audit_rows if getattr(a, "asset_hub_id", None)}

            hub_label_map: dict[int, tuple[str, str]] = {}
            if hub_ids:
                hub_label_map = _build_hub_label_map({int(h) for h in hub_ids if h is not None})

            for a in audit_rows:
                field_raw = (getattr(a, "field_name", "") or "").strip()
                field_lower = field_raw.lower()
                if field_lower in {"updated_at", "created_at"}:
                    continue

                actor = getattr(a.changed_by, "username", None) if getattr(a, "changed_by", None) else None

                hub_pk = getattr(a, "asset_hub_id", None)
                servicer_loan_id, addr = ("", "")
                if hub_pk is not None and int(hub_pk) in hub_label_map:
                    servicer_loan_id, addr = hub_label_map[int(hub_pk)]

                if servicer_loan_id and addr:
                    title = f"{servicer_loan_id} - {addr}"
                elif servicer_loan_id:
                    title = servicer_loan_id
                elif addr:
                    title = addr
                else:
                    title = "Activity"

                field_label = _humanize_field_name(field_raw)
                old_disp = _coalesce_display(getattr(a, "old_value", None), field_raw)
                new_disp = _coalesce_display(getattr(a, "new_value", None), field_raw)
                message = f"{field_label}: {old_disp} → {new_disp}" if old_disp != new_disp else ""

                items.append(
                    {
                        "id": f"audit:{a.id}",
                        "source": "audit",
                        "created_at": a.changed_at,
                        "title": title,
                        "message": message,
                        "field_name": field_raw,
                        "old_value": a.old_value,
                        "new_value": a.new_value,
                        "asset_hub_id": a.asset_hub_id,
                        "actor": actor,
                    }
                )

        items.sort(key=lambda x: x.get("created_at") or timezone.now(), reverse=True)
        items = items[:limit]

        ser = ActivityItemSerializer(items, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)
