"""
Macro Metrics API Views
Exposes macroeconomic indicators from FRED (Federal Reserve Economic Data) to the frontend.

Endpoints:
- GET /api/core/macro/mortgage-rates/30-year - 30-year FRM rate from FRED
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from core.services.macro_metrics_clean import (
    get_mortgage_rate_30_year,
    get_10_year_treasury,
    get_fed_funds_rate,
    get_sofr,
    get_cpi,
    FREDAPIError
)
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_mortgage_30_year_api(request):
    """
    Get current 30-year fixed-rate mortgage average from FRED.
    
    Returns:
        {
            "series_id": "MORTGAGE30US",
            "rate": 6.72,
            "date": "2025-01-02",
            "units": "Percent"
        }
    """
    try:
        data = get_mortgage_rate_30_year()
        return Response(data, status=status.HTTP_200_OK)
    except FREDAPIError as e:
        logger.error(f"Failed to fetch 30-year mortgage rate: {str(e)}")
        return Response(
            {"error": "Failed to fetch mortgage rate data"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_10_year_treasury_api(request):
    """Get 10-Year Treasury Constant Maturity Rate."""
    try:
        data = get_10_year_treasury()
        return Response(data, status=status.HTTP_200_OK)
    except FREDAPIError as e:
        logger.error(f"Failed to fetch 10-year treasury: {str(e)}")
        return Response(
            {"error": "Failed to fetch 10-year treasury data"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_fed_funds_rate_api(request):
    """Get Federal Funds Effective Rate."""
    try:
        data = get_fed_funds_rate()
        return Response(data, status=status.HTTP_200_OK)
    except FREDAPIError as e:
        logger.error(f"Failed to fetch fed funds rate: {str(e)}")
        return Response(
            {"error": "Failed to fetch fed funds rate data"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sofr_api(request):
    """Get Secured Overnight Financing Rate."""
    try:
        data = get_sofr()
        return Response(data, status=status.HTTP_200_OK)
    except FREDAPIError as e:
        logger.error(f"Failed to fetch SOFR: {str(e)}")
        return Response(
            {"error": "Failed to fetch SOFR data"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cpi_api(request):
    """Get Consumer Price Index."""
    try:
        data = get_cpi()
        return Response(data, status=status.HTTP_200_OK)
    except FREDAPIError as e:
        logger.error(f"Failed to fetch CPI: {str(e)}")
        return Response(
            {"error": "Failed to fetch CPI data"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
