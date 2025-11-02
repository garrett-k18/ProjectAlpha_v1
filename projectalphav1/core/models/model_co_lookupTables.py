"""
Centralized Lookup Tables and Choices for Project Alpha

This module defines reusable TextChoices enums used across multiple apps/modules.

What this does:
- Provides centralized choice definitions to ensure data consistency
- Prevents duplicate choice definitions across models
- No database tables created - these are just enums for validation

How to use:
- Import the choices: from core.lookupTables import PropertyType
- Use in models: property_type = models.CharField(max_length=20, choices=PropertyType.choices)

Why this approach:
- DRY principle - define once, use everywhere
- Data consistency - same valid values across all models
- Easy to maintain - update in one place
- No extra database JOINs needed

Django Docs:
- Field Choices: https://docs.djangoproject.com/en/5.2/ref/models/fields/#choices
- Enumeration Types: https://docs.djangoproject.com/en/5.2/ref/models/fields/#enumeration-types
"""

from django.db import models


class PropertyType(models.TextChoices):
    """
    Centralized property type choices used across all modules.
    
    What this does:
    - Defines valid property type values for SellerRawData, HOAAssumption, etc.
    - Provides both value (stored in DB) and label (displayed in UI)
    
    How it works:
    - Format: CONSTANT_NAME = 'db_value', 'Display Label'
    - Use in models: choices=PropertyType.choices
    - Access: PropertyType.SFR returns 'SFR'
    
    Used by:
    - acq_module.models.SellerRawData
    - core.models.HOAAssumption
    - core.models.PropertyTypeBasedAssumption
    - am_module.models.SellerBoardedData
    """
    # Residential property types
    SFR = 'SFR', 'SFR'
    MANUFACTURED = 'Manufactured', 'Manufactured'
    CONDO = 'Condo', 'Condo'
    TOWNHOUSE = 'Townhouse', 'Townhouse'
    TWO_TO_FOUR = '2-4 Family', '2-4 Family'
    MULTIFAMILY = 'Multifamily 5+', 'Multifamily 5+'
    
    # Special use property types
    LAND = 'Land', 'Land'
    
    # Commercial property types
    INDUSTRIAL = 'Industrial', 'Industrial'
    MIXED_USE = 'Mixed Use', 'Mixed Use'
    STORAGE = 'Storage', 'Storage'
    HEALTHCARE = 'Healthcare', 'Healthcare'


# Add more lookup tables here as needed
# Example:
# class OccupancyStatus(models.TextChoices):
#     VACANT = 'Vacant', 'Vacant'
#     OCCUPIED = 'Occupied', 'Occupied'
#     UNKNOWN = 'Unknown', 'Unknown'

