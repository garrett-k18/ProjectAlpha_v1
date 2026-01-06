"""
API view for AM Note Summary.

WHAT: Provides endpoint to retrieve AI-generated note summaries for asset hubs.
WHY: Allows frontend to fetch persisted summaries without regenerating on every load.
HOW: Uses service to generate summary if needed, then returns serialized data.

Docs reviewed:
- DRF APIView: https://www.django-rest-framework.org/api-guide/views/#apiview
- DRF Response: https://www.django-rest-framework.org/api-guide/responses/
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request
from rest_framework import status

from am_module.models.model_am_amData import AMNoteSummary
from am_module.serializers.serial_am_noteSummary import AMNoteSummarySerializer
from am_module.services.serv_am_noteSummary import generate_note_summary


class AMNoteSummaryView(APIView):
    """
    WHAT: API endpoint to get or generate note summary for an asset hub.
    WHY: Provides efficient access to AI summaries with automatic generation.
    HOW: GET endpoint that accepts asset_hub_id query param.
    
    URL: /api/am/notes/summary/?asset_hub_id=<id>
    Method: GET
    Query Params:
        - asset_hub_id (required): ID of the asset hub to get summary for
        - regenerate (optional): If 'true', forces regeneration even if summary exists
    """
    
    permission_classes = [AllowAny]
    authentication_classes: list[type[SessionAuthentication]] = []  # avoid CSRF in dev
    
    def get(self, request: Request) -> Response:
        """
        WHAT: Retrieves or generates note summary for specified asset hub.
        WHY: Provides single endpoint for summary access.
        HOW: Checks for existing summary, generates if needed, returns serialized data.
        
        Args:
            request: DRF request object with query params
            
        Returns:
            Response with serialized summary data or 404 if no notes exist
        """
        # WHAT: Get asset_hub_id from query params
        # WHY: Required to identify which asset's summary to retrieve
        # HOW: Read from request.query_params
        asset_hub_id = request.query_params.get('asset_hub_id')
        
        # WHAT: Validate asset_hub_id is provided
        # WHY: Can't proceed without knowing which asset
        # HOW: Check if param exists and is valid integer
        if not asset_hub_id:
            return Response(
                {"detail": "asset_hub_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            asset_hub_id_int = int(asset_hub_id)
        except (ValueError, TypeError):
            return Response(
                {"detail": "asset_hub_id must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # WHAT: Check if regeneration is requested
        # WHY: Allow manual regeneration via API
        # HOW: Read 'regenerate' query param
        force_regenerate = request.query_params.get('regenerate', '').lower() == 'true'
        
        # WHAT: Check if notes exist before generating summary
        # WHY: Need to distinguish between "no notes" and "generation failed"
        # HOW: Query AMNote model to check if notes exist
        from am_module.models.model_am_amData import AMNote
        note_count = AMNote.objects.filter(asset_hub_id=asset_hub_id_int).count()
        
        # WHAT: Generate or retrieve summary
        # WHY: Ensures summary exists and is current
        # HOW: Call generate_note_summary service with error handling
        try:
            summary = generate_note_summary(asset_hub_id_int, force_regenerate=force_regenerate)
        except Exception as e:
            # WHAT: Log error and return error response
            # WHY: Frontend needs to know if generation failed
            # HOW: Return 200 with error details (so frontend can display it)
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"Error generating summary for asset hub {asset_hub_id_int}")
            
            # WHAT: Extract more detailed error message
            # WHY: Help user understand what went wrong
            # HOW: Get error message and any additional context
            error_msg = str(e)
            if hasattr(e, '__cause__') and e.__cause__:
                error_msg = f"{error_msg} (Caused by: {str(e.__cause__)})"
            
            return Response(
                {
                    "detail": f"Failed to generate summary: {error_msg}",
                    "summary_text": "",
                    "bullets": [],
                    "note_count": note_count,
                    "error": True,
                },
                status=status.HTTP_200_OK  # Return 200 so frontend can display error
            )
        
        # WHAT: Handle case where no summary exists
        # WHY: Could be no notes OR generation failed
        # HOW: Check note count to provide accurate message
        if summary is None:
            if note_count == 0:
                # WHAT: No notes exist
                # WHY: Can't generate summary without notes
                # HOW: Return message indicating no notes
                return Response(
                    {
                        "detail": "No notes found for this asset hub",
                        "summary_text": "",
                        "bullets": [],
                        "note_count": 0,
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # WHAT: Notes exist but summary generation failed
                # WHY: Generation may have failed silently
                # HOW: Return error indicating generation issue
                return Response(
                    {
                        "detail": f"Summary generation failed. {note_count} notes exist but summary could not be generated.",
                        "summary_text": "",
                        "bullets": [],
                        "note_count": note_count,
                        "error": True,
                    },
                    status=status.HTTP_200_OK
                )
        
        # WHAT: Serialize summary for API response
        # WHY: Frontend expects structured JSON
        # HOW: Use AMNoteSummarySerializer
        serializer = AMNoteSummarySerializer(summary)
        
        # WHAT: Return serialized data
        # WHY: Standard DRF response format
        # HOW: Return Response with serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)

