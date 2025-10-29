"""
Macro Metrics Service
Fetches macroeconomic indicators from FRED (Federal Reserve Economic Data).

API Documentation: https://fred.stlouisfed.org/docs/api/fred/
Base URL: https://api.stlouisfed.org/fred
"""
import requests
from typing import Dict, Optional, Any
from django.core.cache import cache
import logging
import os

logger = logging.getLogger(__name__)

# FRED API Configuration (Federal Reserve Economic Data)
FRED_API_KEY = os.getenv("FRED_API_KEY")
FRED_BASE_URL = "https://api.stlouisfed.org/fred"
CACHE_TIMEOUT = 86400  # 24 hours cache for rates (86400 seconds)

# FRED Series IDs
FRED_MORTGAGE_30_YEAR = "MORTGAGE30US"  # 30-Year Fixed Rate Mortgage Average
FRED_10_YEAR_TREASURY = "DGS10"  # 10-Year Treasury Constant Maturity Rate
FRED_FED_FUNDS_RATE = "DFF"  # Federal Funds Effective Rate
FRED_SOFR = "SOFR"  # Secured Overnight Financing Rate
FRED_CPI = "CPIAUCSL"  # Consumer Price Index for All Urban Consumers: All Items


class FREDAPIError(Exception):
    """Custom exception for FRED API errors"""
    pass


def _make_fred_request(endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Make a request to FRED API with proper parameters and error handling.
    
    Args:
        endpoint: API endpoint (e.g., 'series/observations')
        params: Query parameters as dictionary
    
    Returns:
        JSON response as dictionary
    
    Raises:
        FREDAPIError: If the API request fails
    """
    # Check if API key is available
    if not FRED_API_KEY:
        logger.error("FRED_API_KEY environment variable not set!")
        raise FREDAPIError("FRED API key not configured")
    
    url = f"{FRED_BASE_URL}/{endpoint}"
    
    # Add API key and default file_type to params
    request_params = params.copy() if params else {}
    request_params['api_key'] = FRED_API_KEY
    request_params['file_type'] = 'json'
    
    try:
        response = requests.get(url, params=request_params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"FRED API HTTP error: {e.response.status_code} - {e.response.text}")
        raise FREDAPIError(f"API request failed: {e.response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"FRED API request error: {str(e)}")
        raise FREDAPIError(f"Network error: {str(e)}")
    except ValueError as e:
        logger.error(f"FRED API JSON parse error: {str(e)}")
        raise FREDAPIError("Invalid JSON response from API")


def get_mortgage_rate_30_year() -> Dict[str, Any]:
    """
    Get the current 30-year fixed-rate mortgage average from FRED.
    
    Returns:
        Dictionary with rate information:
        {
            'series_id': 'MORTGAGE30US',
            'rate': 6.72,
            'date': '2025-01-02',
            'units': 'Percent'
        }
    
    Uses caching to avoid excessive API calls (24 hour cache).
    """
    cache_key = "fred_api:mortgage_30_year"
    
    # Check cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.info("Returning cached 30-year mortgage rate")
        return cached_data
    
    # Fetch from FRED API
    logger.info("Fetching 30-year mortgage rate from FRED API")
    try:
        # Get the 2 most recent observations to calculate change
        params = {
            'series_id': FRED_MORTGAGE_30_YEAR,
            'sort_order': 'desc',  # Most recent first
            'limit': 2  # Get latest 2 values for change calculation
        }
        
        response = _make_fred_request("series/observations", params=params)
        
        # Extract the observation data
        if 'observations' in response and len(response['observations']) > 0:
            current_obs = response['observations'][0]
            current_rate = float(current_obs['value']) if current_obs['value'] != '.' else None
            
            # Calculate percentage change from previous observation
            change_pct = None
            previous_rate = None
            previous_date = None
            
            if len(response['observations']) > 1 and current_rate is not None:
                previous_obs = response['observations'][1]
                previous_rate = float(previous_obs['value']) if previous_obs['value'] != '.' else None
                previous_date = previous_obs['date']
                
                if previous_rate is not None and previous_rate != 0:
                    change_pct = ((current_rate - previous_rate) / previous_rate) * 100
                    # Log for debugging
                    logger.info(f"Mortgage rate change: {current_rate} vs {previous_rate} = {change_pct:.4f}% (dates: {current_obs['date']} vs {previous_date})")
            
            data = {
                'series_id': FRED_MORTGAGE_30_YEAR,
                'rate': current_rate,
                'date': current_obs['date'],
                'units': 'Percent',
                'change_pct': change_pct,  # Week-over-week change
                'previous_rate': previous_rate,
                'previous_date': previous_date
            }
            
            # Cache the result
            cache.set(cache_key, data, CACHE_TIMEOUT)
            
            return data
        else:
            raise FREDAPIError("No observations returned from FRED API")
            
    except FREDAPIError as e:
        logger.error(f"Failed to fetch 30-year mortgage rate: {str(e)}")
        raise


def get_fred_series(series_id: str, series_name: str) -> Dict[str, Any]:
    """
    Generic function to fetch any FRED series with week-over-week change.
    
    Args:
        series_id: FRED series identifier
        series_name: Human-readable name for caching
    
    Returns:
        Dictionary with current value, date, and percentage change
    """
    cache_key = f"fred_api:{series_name}"
    
    # Check cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.info(f"Returning cached {series_name}")
        return cached_data
    
    # Fetch from FRED API
    logger.info(f"Fetching {series_name} from FRED API")
    try:
        # Get the 2 most recent observations to calculate change
        params = {
            'series_id': series_id,
            'sort_order': 'desc',  # Most recent first
            'limit': 2  # Get latest 2 values for change calculation
        }
        
        response = _make_fred_request("series/observations", params=params)
        
        # Extract the observation data
        if 'observations' in response and len(response['observations']) > 0:
            current_obs = response['observations'][0]
            current_value = float(current_obs['value']) if current_obs['value'] != '.' else None
            
            # Calculate percentage change from previous observation
            change_pct = None
            previous_value = None
            previous_date = None
            
            if len(response['observations']) > 1 and current_value is not None:
                previous_obs = response['observations'][1]
                previous_value = float(previous_obs['value']) if previous_obs['value'] != '.' else None
                previous_date = previous_obs['date']
                
                if previous_value is not None and previous_value != 0:
                    change_pct = ((current_value - previous_value) / previous_value) * 100
                    logger.info(f"{series_name} change: {current_value} vs {previous_value} = {change_pct:.4f}% (dates: {current_obs['date']} vs {previous_date})")
            
            data = {
                'series_id': series_id,
                'value': current_value,
                'date': current_obs['date'],
                'change_pct': change_pct,
                'previous_value': previous_value,
                'previous_date': previous_date
            }
            
            # Cache the result
            cache.set(cache_key, data, CACHE_TIMEOUT)
            
            return data
        else:
            raise FREDAPIError(f"No observations returned from FRED API for {series_name}")
            
    except FREDAPIError as e:
        logger.error(f"Failed to fetch {series_name}: {str(e)}")
        raise


def get_10_year_treasury() -> Dict[str, Any]:
    """Get 10-Year Treasury Constant Maturity Rate."""
    return get_fred_series(FRED_10_YEAR_TREASURY, "10_year_treasury")


def get_fed_funds_rate() -> Dict[str, Any]:
    """Get Federal Funds Effective Rate."""
    return get_fred_series(FRED_FED_FUNDS_RATE, "fed_funds_rate")


def get_sofr() -> Dict[str, Any]:
    """Get Secured Overnight Financing Rate."""
    return get_fred_series(FRED_SOFR, "sofr")


def get_cpi() -> Dict[str, Any]:
    """Get Consumer Price Index."""
    return get_fred_series(FRED_CPI, "cpi")


def clear_rate_cache():
    """
    Clear all cached FRED data.
    """
    cache.delete_pattern("fred_api:*")
    logger.info("Cleared all FRED API caches")
