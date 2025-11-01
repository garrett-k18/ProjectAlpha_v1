"""
API views for assumptions management (StateReference, FCTimelines, etc.)

What this does:
- Provides REST API endpoints for frontend to fetch and update assumptions
- Handles GET requests to load data and PUT/PATCH requests to save edits
- Supports bulk updates for efficient saving of multiple state records

Location: projectalphav1/core/views/views_assumptions.py
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from django.http import HttpResponse
from django.conf import settings
import csv
from io import TextIOWrapper

from core.models import StateReference, FCTimelines, FCStatus, CommercialUnits, Servicer
from core.serializers.assumptions import (
    StateReferenceSerializer,
    FCTimelinesSerializer,
    FCStatusSerializer,
    CommercialUnitsSerializer,
    ServicerSerializer,
)


class DevAuthBypassMixin:
    """
    Development-only auth bypass.
    What: When settings.DEBUG is True, disables DRF permission checks so devs don't need tokens/logins.
    Why: Speeds up local development and scripted imports without authentication friction.
    How: Overrides get_permissions(); in DEBUG returns an empty list (AllowAny), otherwise defers to normal behavior.
    Where: Applied to all ViewSets in this module.
    """
    def get_permissions(self):  # type: ignore[override]
        if getattr(settings, 'DEBUG', False):
            return []
        return super().get_permissions()

    def get_authenticators(self):  # type: ignore[override]
        """
        In DEBUG, disable DRF authenticators entirely so that SessionAuthentication
        is not applied and CSRF is not enforced for API calls from the front-end dev server.
        """
        if getattr(settings, 'DEBUG', False):
            return []
        return super().get_authenticators()


class StateReferenceViewSet(DevAuthBypassMixin, viewsets.ModelViewSet):
    """
    API ViewSet for StateReference model

    What this does:
    - GET /api/core/state-assumptions/ - Returns all states with their assumptions
    - PUT /api/core/state-assumptions/{state_code}/ - Updates a single state
    - POST /api/core/state-assumptions/bulk_update/ - Updates multiple states at once

    How it works:
    - Frontend loads all states on page load
    - Users edit fields inline in the table
    - Frontend sends bulk update with all changed states
    - Backend validates and saves all changes in a transaction
    """

    queryset = StateReference.objects.all().order_by("state_name")
    serializer_class = StateReferenceSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = "state_code"  # Use state_code instead of id for lookups
    pagination_class = None  # Disable pagination - only ~51 states, return all at once

    def get_queryset(self):
        """Get all state references, optionally filtered by query params"""
        queryset = StateReference.objects.all().order_by("state_name")

        # Optional: Filter by judicial status
        judicial = self.request.query_params.get("judicial", None)
        if judicial is not None:
            is_judicial = judicial.lower() == "true"
            queryset = queryset.filter(judicialvsnonjudicial=is_judicial)

        return queryset

    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        """
        Return all states without pagination for UI option lists.

        Why: UI multi-selects need the complete list (≈51 including PR) without
        dealing with pagination. Keeping this separate avoids changing default
        pagination for the standard list endpoint.
        """
        states = self.get_queryset()
        serializer = StateReferenceSerializer(states, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def bulk_update(self, request):
        """
        Bulk update multiple state assumptions at once

        Expected request body:
        [
            {"code": "AL", "fcStateMonths": 12, "evictionDuration": 3, ...},
            {"code": "AK", "fcStateMonths": 15, ...},
        ]

        Returns:
        - 200 OK with updated records on success
        - 400 Bad Request with validation errors on failure
        """
        states_data = request.data

        if not isinstance(states_data, list):
            return Response(
                {"error": "Expected a list of state records"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_states = []
        errors = []

        # Use transaction to ensure all updates succeed or none do
        try:
            with transaction.atomic():
                for state_data in states_data:
                    state_code = state_data.get("code")

                    if not state_code:
                        errors.append({"error": "Missing state code", "data": state_data})
                        continue

                    try:
                        # Get the state instance
                        state_instance = StateReference.objects.get(state_code=state_code)

                        # Update with serializer (validates data)
                        serializer = StateReferenceSerializer(
                            state_instance, data=state_data, partial=True
                        )

                        if serializer.is_valid():
                            serializer.save()
                            updated_states.append(serializer.data)
                        else:
                            errors.append(
                                {
                                    "state_code": state_code,
                                    "errors": serializer.errors,
                                }
                            )

                    except StateReference.DoesNotExist:
                        errors.append(
                            {
                                "error": f"State {state_code} not found",
                                "state_code": state_code,
                            }
                        )

                # If there are any errors, rollback the transaction
                if errors:
                    raise Exception("Validation errors occurred")

        except Exception as e:
            return Response(
                {
                    "error": "Bulk update failed",
                    "details": errors,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": f"Successfully updated {len(updated_states)} states",
                "updated": updated_states,
            },
            status=status.HTTP_200_OK,
        )


class FCTimelinesViewSet(DevAuthBypassMixin, viewsets.ModelViewSet):
    """
    API ViewSet for FCTimelines model

    Endpoints:
    - GET /api/core/fc-timelines/
    - GET /api/core/fc-timelines/?state=AL
    - GET /api/core/fc-timelines/matrix/
    - POST /api/core/fc-timelines/bulk_update/
    - POST /api/core/fc-timelines/bulk_set_status_duration/
    - GET /api/core/fc-timelines/matrix_csv/
    - POST /api/core/fc-timelines/import_matrix_csv/
    """

    queryset = FCTimelines.objects.all().select_related("state", "fc_status")
    serializer_class = FCTimelinesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter timelines by state if provided"""
        queryset = FCTimelines.objects.all().select_related("state", "fc_status")

        state_code = self.request.query_params.get("state", None)
        if state_code:
            queryset = queryset.filter(state__state_code=state_code)

        return queryset.order_by("state__state_name", "fc_status__order")

    @action(detail=False, methods=["get"])
    def matrix(self, request):
        """
        Return foreclosure timelines in matrix format for easy table display

        Response format:
        {"states": [..], "statuses": [{ id, status, statusDisplay, order, timelines: { AL: {...} } }]}

        Always returns full cross of states × statuses. Missing rows are placeholders.
        """
        states = StateReference.objects.all().order_by("state_name")
        state_codes = [s.state_code for s in states]
        # Build per-state metadata for frontend (e.g., Judicial vs Non-Judicial)
        # This allows the UI to show a "State Type" row above status rows without
        # duplicating business logic client-side.
        state_meta = {
            s.state_code: {
                "name": s.state_name,
                "judicial": bool(getattr(s, "judicialvsnonjudicial", False)),
                "typeDisplay": "Judicial" if getattr(s, "judicialvsnonjudicial", False) else "Non-Judicial",
            }
            for s in states
        }

        fc_statuses = FCStatus.objects.all().order_by("order")
        timelines = FCTimelines.objects.all().select_related("state", "fc_status")

        matrix_data = []

        # Normal path: have FCStatus rows
        for fc_status in fc_statuses:
            status_timelines = timelines.filter(fc_status=fc_status)
            timelines_by_state = {}

            existing_timelines = {
                t.state.state_code: t for t in status_timelines
            }

            for code in state_codes:
                t = existing_timelines.get(code)
                if t:
                    timelines_by_state[code] = {
                        "id": t.id,
                        "durationDays": t.duration_days,
                        "costAvg": float(t.cost_avg) if t.cost_avg else None,
                        "notes": t.notes or "",
                    }
                else:
                    timelines_by_state[code] = {
                        "id": None,
                        "durationDays": None,
                        "costAvg": None,
                        "notes": "",
                        "stateCode": code,
                        "statusId": fc_status.id,
                    }

            matrix_data.append(
                {
                    "id": fc_status.id,
                    "status": fc_status.status,
                    "statusDisplay": fc_status.get_status_display(),
                    "order": fc_status.order,
                    "timelines": timelines_by_state,
                }
            )

        # Fallback: no FCStatus rows — use STATUS_CHOICES
        if not matrix_data:
            for idx, (code, display) in enumerate(FCStatus.STATUS_CHOICES, start=1):
                timelines_by_state = {}
                for st_code in state_codes:
                    timelines_by_state[st_code] = {
                        "id": None,
                        "durationDays": None,
                        "costAvg": None,
                        "notes": "",
                        "stateCode": st_code,
                        "statusId": None,
                        "statusCode": code,
                    }
                matrix_data.append(
                    {
                        "id": None,
                        "status": code,
                        "statusDisplay": display,
                        "order": idx,
                        "timelines": timelines_by_state,
                    }
                )

        return Response({
            "states": state_codes,
            "statuses": matrix_data,
            "stateMeta": state_meta,
        })

    @action(detail=False, methods=["post"])
    def bulk_update(self, request):
        """Bulk update multiple foreclosure timelines at once"""
        timelines_data = request.data

        if not isinstance(timelines_data, list):
            return Response(
                {"error": "Expected a list of timeline records"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_timelines = []
        errors = []

        try:
            with transaction.atomic():
                for timeline_data in timelines_data:
                    timeline_id = timeline_data.get("id")
                    if not timeline_id:
                        errors.append(
                            {"error": "Missing timeline id", "data": timeline_data}
                        )
                        continue

                    try:
                        instance = FCTimelines.objects.get(id=timeline_id)
                        serializer = FCTimelinesSerializer(
                            instance, data=timeline_data, partial=True
                        )
                        if serializer.is_valid():
                            serializer.save()
                            updated_timelines.append(serializer.data)
                        else:
                            errors.append(
                                {
                                    "timeline_id": timeline_id,
                                    "errors": serializer.errors,
                                }
                            )
                    except FCTimelines.DoesNotExist:
                        errors.append(
                            {
                                "error": f"Timeline {timeline_id} not found",
                                "timeline_id": timeline_id,
                            }
                        )

                if errors:
                    raise Exception("Validation errors occurred")
        except Exception as e:
            return Response(
                {
                    "error": "Bulk update failed",
                    "details": errors,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": f"Successfully updated {len(updated_timelines)} timelines",
                "updated": updated_timelines,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def bulk_set_status_duration(self, request):
        """
        Bulk set duration_days for ALL states for a given foreclosure status.
        Body supports either {statusId} or {statusCode} and {durationDays}.
        """
        status_id = request.data.get("statusId")
        status_code = request.data.get("statusCode")
        duration_days = request.data.get("durationDays")
        create_missing = request.data.get("createMissing", True)

        try:
            if duration_days is None:
                raise ValueError("durationDays is required")
            duration_days = int(duration_days)
            if duration_days < 0:
                raise ValueError("durationDays must be >= 0")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Resolve or create FCStatus
        fc_status = None
        if status_id:
            try:
                fc_status = FCStatus.objects.get(id=status_id)
            except FCStatus.DoesNotExist:
                return Response(
                    {"error": f"FCStatus id={status_id} not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif status_code:
            fc_status = FCStatus.objects.filter(status=status_code).first()
            if not fc_status:
                choice_index = None
                display_name = None
                for idx, (code, display) in enumerate(FCStatus.STATUS_CHOICES, start=1):
                    if code == status_code:
                        choice_index = idx
                        display_name = display
                        break
                if choice_index is None:
                    return Response(
                        {"error": f"Unknown statusCode \"{status_code}\""},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                fc_status = FCStatus.objects.create(
                    status=status_code,
                    order=choice_index,
                    notes=f"Autocreated for bulk set ({display_name})",
                )
        else:
            return Response(
                {"error": "Provide statusId or statusCode"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated = 0
        created = 0
        try:
            with transaction.atomic():
                for state in StateReference.objects.all():
                    timeline = FCTimelines.objects.filter(
                        state=state, fc_status=fc_status
                    ).first()
                    if not timeline:
                        if not create_missing:
                            continue
                        timeline = FCTimelines(state=state, fc_status=fc_status)
                        created += 1
                    else:
                        updated += 1
                    timeline.duration_days = duration_days
                    timeline.save()
        except Exception as e:
            return Response(
                {"error": "Bulk set failed", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "Bulk set completed",
                "statusId": fc_status.id,
                "statusCode": fc_status.status,
                "durationDays": duration_days,
                "updatedCount": updated,
                "createdCount": created,
            }
        )

    @action(detail=False, methods=["get"])
    def matrix_csv(self, request):
        """
        Export the foreclosure timelines matrix as a CSV template.
        Columns: state_code,state_name,status_code,status_display,duration_days,cost_avg,notes
        """
        states = StateReference.objects.all().order_by("state_name")
        fc_statuses = FCStatus.objects.all().order_by("order")
        timelines = FCTimelines.objects.all().select_related("state", "fc_status")

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="fc_timelines_matrix.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(
            [
                "state_code",
                "state_name",
                "status_code",
                "status_display",
                "duration_days",
                "cost_avg",
                "notes",
            ]
        )

        if fc_statuses.exists():
            for st in states:
                st_timelines = {t.fc_status_id: t for t in timelines if t.state_id == st.id}
                for fc in fc_statuses:
                    t = st_timelines.get(fc.id)
                    writer.writerow(
                        [
                            st.state_code,
                            st.state_name,
                            fc.status,
                            fc.get_status_display(),
                            t.duration_days if t else "",
                            (f"{t.cost_avg:.2f}" if t and t.cost_avg is not None else ""),
                            (t.notes if t and t.notes else ""),
                        ]
                    )
        else:
            for st in states:
                for code, display in FCStatus.STATUS_CHOICES:
                    writer.writerow([st.state_code, st.state_name, code, display, "", "", ""])

        return response

    @action(detail=False, methods=["post"])
    def import_matrix_csv(self, request):
        """
        Import (upsert) foreclosure timelines from a CSV matrix (same format as matrix_csv).
        Expected upload (multipart/form-data): file=<csv>
        """
        if "file" not in request.FILES:
            return Response(
                {"error": "No file uploaded. Use form field name \"file\"."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file = request.FILES["file"]
        try:
            csv_file = TextIOWrapper(file.file, encoding="utf-8")
            reader = csv.DictReader(csv_file)
        except Exception as e:
            return Response(
                {"error": f"Invalid CSV upload: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created = 0
        updated = 0
        errors = []

        def get_or_create_status_by_code(code: str) -> FCStatus:
            fc = FCStatus.objects.filter(status=code).first()
            if fc:
                return fc
            for idx, (c, display) in enumerate(FCStatus.STATUS_CHOICES, start=1):
                if c == code:
                    return FCStatus.objects.create(
                        status=code,
                        order=idx,
                        notes=f"Autocreated from CSV import ({display})",
                    )
            raise ValueError(f"Unknown status_code \"{code}\"")

        try:
            with transaction.atomic():
                for i, row in enumerate(reader, start=2):
                    try:
                        state_code = (row.get("state_code") or "").strip()
                        status_code = (row.get("status_code") or "").strip()
                        if not state_code or not status_code:
                            raise ValueError("Missing required state_code or status_code")

                        try:
                            st = StateReference.objects.get(state_code=state_code)
                        except StateReference.DoesNotExist:
                            raise ValueError(f"Unknown state_code \"{state_code}\"")

                        fc = get_or_create_status_by_code(status_code)

                        duration_days = row.get("duration_days")
                        duration_days = (
                            int(duration_days)
                            if (duration_days and str(duration_days).strip() != "")
                            else None
                        )
                        cost_avg = row.get("cost_avg")
                        cost_avg = (
                            float(cost_avg)
                            if (cost_avg and str(cost_avg).strip() != "")
                            else None
                        )
                        notes = (row.get("notes") or "").strip()

                        timeline, created_flag = FCTimelines.objects.get_or_create(
                            state=st, fc_status=fc
                        )
                        if created_flag:
                            created += 1
                        else:
                            updated += 1
                        timeline.duration_days = duration_days
                        timeline.cost_avg = cost_avg
                        timeline.notes = notes
                        timeline.save()
                    except Exception as row_err:
                        errors.append({"row": i, "error": str(row_err), "data": row})
                if errors:
                    raise Exception("Errors during CSV import")
        except Exception as e:
            return Response(
                {"error": "Import failed", "message": str(e), "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Import successful", "created": created, "updated": updated}
        )


class FCStatusViewSet(DevAuthBypassMixin, viewsets.ReadOnlyModelViewSet):
    """Read-only endpoints for foreclosure statuses"""
    queryset = FCStatus.objects.all().order_by("order")
    serializer_class = FCStatusSerializer
    permission_classes = [IsAuthenticated]


class CommercialUnitsViewSet(DevAuthBypassMixin, viewsets.ModelViewSet):
    """CRUD for CommercialUnits model"""
    queryset = CommercialUnits.objects.all().order_by("units")
    serializer_class = CommercialUnitsSerializer
    permission_classes = [IsAuthenticated]


class ServicerViewSet(DevAuthBypassMixin, viewsets.ModelViewSet):
    """CRUD for Servicer model"""
    queryset = Servicer.objects.all().order_by("servicer_name")
    serializer_class = ServicerSerializer
    permission_classes = [IsAuthenticated]
