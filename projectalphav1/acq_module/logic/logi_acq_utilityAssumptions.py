"""
Utility and Property Management Assumption Workflow Logic

This module implements the assumption workflow with the following priority order:
1. Square footage-based assumptions (highest priority)
2. Unit-based assumptions (for multifamily when sqft not available)
3. State-specific assumptions (middle priority)
4. Property type assumptions (lowest priority/fallback)

The workflow determines which assumption source to use based on available data
and applies the appropriate calculations.
"""

from decimal import Decimal
from typing import Dict, Optional, Tuple
from django.db.models import Q

from acq_module.models.model_acq_seller import SellerRawData
from core.models.model_co_assumptions import (
    PropertyTypeAssumption,
    SquareFootageAssumption,
    UnitBasedAssumption,
    StateReference
)


class UtilityAssumptionWorkflow:
    """
    Main workflow class for determining utility and property management assumptions.
    
    What this does:
    - Implements the priority-based assumption workflow
    - Determines which assumption source to use based on available data
    - Calculates monthly and one-time costs using the appropriate method
    
    How it works:
    - Check for square footage data first (highest priority)
    - Fall back to unit count for multifamily properties
    - Use state-specific assumptions if available
    - Use property type assumptions as final fallback
    """
    
    def __init__(self, asset_hub_id: int):
        """
        Initialize the workflow for a specific asset.
        
        Args:
            asset_hub_id: The AssetIdHub primary key
        """
        self.asset_hub_id = asset_hub_id
        self._seller_data = None
        self._state_reference = None
    
    @property
    def seller_data(self) -> Optional[SellerRawData]:
        """Get seller raw data for this asset (cached)."""
        if self._seller_data is None:
            try:
                self._seller_data = SellerRawData.objects.get(asset_hub_id=self.asset_hub_id)
            except SellerRawData.DoesNotExist:
                self._seller_data = None
        return self._seller_data
    
    @property
    def state_reference(self) -> Optional[StateReference]:
        """Get state reference data for this asset (cached)."""
        if self._state_reference is None and self.seller_data:
            try:
                self._state_reference = StateReference.objects.get(
                    state_code=self.seller_data.state
                )
            except StateReference.DoesNotExist:
                self._state_reference = None
        return self._state_reference
    
    def get_property_category(self) -> str:
        """
        Determine if property is residential or commercial.
        
        Returns:
            str: 'RESIDENTIAL' or 'COMMERCIAL'
        """
        if not self.seller_data or not self.seller_data.property_type:
            return 'RESIDENTIAL'  # Default to residential
        
        # Commercial property types
        commercial_types = [
            SellerRawData.PropertyType.INDUSTRIAL,
            SellerRawData.PropertyType.MIXED_USE,
            SellerRawData.PropertyType.STORAGE,
            SellerRawData.PropertyType.HEALTHCARE,
        ]
        
        if self.seller_data.property_type in commercial_types:
            return 'COMMERCIAL'
        
        return 'RESIDENTIAL'
    
    def get_square_footage(self) -> Optional[int]:
        """
        Get square footage for the property.
        
        Returns:
            Optional[int]: Square footage if available
        """
        if not self.seller_data:
            return None
        
        # For commercial properties, use gross square footage
        if self.get_property_category() == 'COMMERCIAL':
            return getattr(self.seller_data, 'gross_square_footage', None)
        
        # For residential properties, use livable square footage
        return getattr(self.seller_data, 'livable_square_ft_building', None)
    
    def get_unit_count(self) -> Optional[int]:
        """
        Get unit count for multifamily properties.
        
        Returns:
            Optional[int]: Unit count if available and applicable
        """
        if not self.seller_data:
            return None
        
        # Only applicable for multifamily properties
        multifamily_types = [
            SellerRawData.PropertyType.TWO_TO_FOUR,
            SellerRawData.PropertyType.MULTIFAMILY,
        ]
        
        if self.seller_data.property_type not in multifamily_types:
            return None
        
        return getattr(self.seller_data, 'units', None)
    
    def get_square_footage_assumption(self) -> Optional[SquareFootageAssumption]:
        """
        Get the appropriate square footage-based assumption.
        
        Returns:
            Optional[SquareFootageAssumption]: Matching assumption if found
        """
        square_footage = self.get_square_footage()
        if not square_footage:
            return None
        
        property_category = self.get_property_category()
        
        # Get the first active square footage assumption for the property category
        # Since we no longer use ranges, we just need one assumption per category
        try:
            return SquareFootageAssumption.objects.get(
                property_category=property_category,
                is_active=True
            )
        except SquareFootageAssumption.DoesNotExist:
            return None
        except SquareFootageAssumption.MultipleObjectsReturned:
            # If multiple exist, get the first one ordered by description
            return SquareFootageAssumption.objects.filter(
                property_category=property_category,
                is_active=True
            ).order_by('description').first()
    
    def get_unit_based_assumption(self) -> Optional[UnitBasedAssumption]:
        """
        Get the appropriate unit-based assumption.
        
        Returns:
            Optional[UnitBasedAssumption]: Matching assumption if found
        """
        unit_count = self.get_unit_count()
        if not unit_count:
            return None
        
        # Find matching unit-based assumption
        assumptions = UnitBasedAssumption.objects.filter(
            is_active=True
        ).order_by('units_min')
        
        for assumption in assumptions:
            if assumption.matches_unit_count(unit_count):
                return assumption
        
        return None
    
    def get_property_type_assumption(self) -> Optional[PropertyTypeAssumption]:
        """
        Get the property type-based assumption.
        
        Returns:
            Optional[PropertyTypeAssumption]: Matching assumption if found
        """
        if not self.seller_data or not self.seller_data.property_type:
            return None
        
        try:
            return PropertyTypeAssumption.objects.get(
                property_type=self.seller_data.property_type,
                is_active=True
            )
        except PropertyTypeAssumption.DoesNotExist:
            return None
    
    def determine_assumption_source(self) -> Tuple[str, object]:
        """
        Determine which assumption source to use based on priority.
        
        Returns:
            Tuple[str, object]: (source_type, assumption_object)
            source_type can be: 'square_footage', 'unit_based', 'state', 'property_type', 'none'
        """
        # Priority 1: Square footage-based assumptions
        sqft_assumption = self.get_square_footage_assumption()
        if sqft_assumption:
            return ('square_footage', sqft_assumption)
        
        # Priority 2: Unit-based assumptions (for multifamily)
        unit_assumption = self.get_unit_based_assumption()
        if unit_assumption:
            return ('unit_based', unit_assumption)
        
        # Priority 3: State-specific assumptions
        if self.state_reference:
            return ('state', self.state_reference)
        
        # Priority 4: Property type assumptions (fallback)
        property_type_assumption = self.get_property_type_assumption()
        if property_type_assumption:
            return ('property_type', property_type_assumption)
        
        return ('none', None)
    
    def calculate_assumptions(self) -> Dict[str, Decimal]:
        """
        Calculate all utility and property management assumptions.
        
        Returns:
            Dict[str, Decimal]: Dictionary containing all calculated costs
        """
        source_type, assumption_obj = self.determine_assumption_source()
        
        if source_type == 'none':
            # Return zero costs if no assumptions found
            return self._get_zero_costs()
        
        if source_type == 'square_footage':
            return self._calculate_from_square_footage(assumption_obj)
        elif source_type == 'unit_based':
            return self._calculate_from_units(assumption_obj)
        elif source_type == 'state':
            return self._calculate_from_state(assumption_obj)
        elif source_type == 'property_type':
            return self._calculate_from_property_type(assumption_obj)
        
        return self._get_zero_costs()
    
    def _calculate_from_square_footage(self, assumption: SquareFootageAssumption) -> Dict[str, Decimal]:
        """Calculate costs using square footage-based assumption."""
        square_footage = self.get_square_footage()
        if not square_footage:
            return self._get_zero_costs()
        
        monthly_costs = assumption.calculate_monthly_costs(square_footage)
        one_time_costs = assumption.calculate_one_time_costs(square_footage)
        
        return {
            **monthly_costs,
            **one_time_costs,
            'source_type': 'square_footage',
            'source_description': str(assumption),
        }
    
    def _calculate_from_units(self, assumption: UnitBasedAssumption) -> Dict[str, Decimal]:
        """Calculate costs using unit-based assumption."""
        unit_count = self.get_unit_count()
        if not unit_count:
            return self._get_zero_costs()
        
        monthly_costs = assumption.calculate_monthly_costs(unit_count)
        one_time_costs = assumption.calculate_one_time_costs(unit_count)
        
        return {
            **monthly_costs,
            **one_time_costs,
            'source_type': 'unit_based',
            'source_description': str(assumption),
        }
    
    def _calculate_from_state(self, state_ref: StateReference) -> Dict[str, Decimal]:
        """Calculate costs using state-specific assumption."""
        return {
            'utility_electric': state_ref.utility_electric_avg,
            'utility_gas': state_ref.utility_gas_avg,
            'utility_water': state_ref.utility_water_avg,
            'utility_sewer': state_ref.utility_sewer_avg,
            'utility_trash': state_ref.utility_trash_avg,
            'utility_other': state_ref.utility_other_avg,
            'property_management': state_ref.property_management_avg,
            'repairs_maintenance': state_ref.repairs_maintenance_avg,
            'marketing': state_ref.marketing_avg,
            'security_cost': state_ref.security_cost_avg,
            'landscaping': state_ref.landscaping_avg,
            'pool_maintenance': state_ref.pool_maintenance_avg,
            'trashout': state_ref.trashout_cost_avg,
            'renovation': state_ref.renovation_cost_avg,
            'source_type': 'state',
            'source_description': f"State: {state_ref.state_name}",
        }
    
    def _calculate_from_property_type(self, assumption: PropertyTypeAssumption) -> Dict[str, Decimal]:
        """Calculate costs using property type assumption."""
        return {
            'utility_electric': assumption.utility_electric_monthly,
            'utility_gas': assumption.utility_gas_monthly,
            'utility_water': assumption.utility_water_monthly,
            'utility_sewer': assumption.utility_sewer_monthly,
            'utility_trash': assumption.utility_trash_monthly,
            'utility_other': assumption.utility_other_monthly,
            'property_management': assumption.property_management_monthly,
            'repairs_maintenance': assumption.repairs_maintenance_monthly,
            'marketing': assumption.marketing_monthly,
            'security_cost': assumption.security_cost_monthly,
            'landscaping': assumption.landscaping_monthly,
            'pool_maintenance': assumption.pool_maintenance_monthly,
            'trashout': assumption.trashout_cost,
            'renovation': assumption.renovation_cost,
            'source_type': 'property_type',
            'source_description': str(assumption),
        }
    
    def _get_zero_costs(self) -> Dict[str, Decimal]:
        """Return dictionary with all costs set to zero."""
        return {
            'utility_electric': Decimal('0.00'),
            'utility_gas': Decimal('0.00'),
            'utility_water': Decimal('0.00'),
            'utility_sewer': Decimal('0.00'),
            'utility_trash': Decimal('0.00'),
            'utility_other': Decimal('0.00'),
            'property_management': Decimal('0.00'),
            'repairs_maintenance': Decimal('0.00'),
            'marketing': Decimal('0.00'),
            'security_cost': Decimal('0.00'),
            'landscaping': Decimal('0.00'),
            'pool_maintenance': Decimal('0.00'),
            'trashout': Decimal('0.00'),
            'renovation': Decimal('0.00'),
            'source_type': 'none',
            'source_description': 'No assumptions found',
        }


# Utility functions for the individual assumption functions requested

def utility_electric(asset_hub_id: int) -> Decimal:
    """
    Get electric utility assumption for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Monthly electric utility cost
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    assumptions = workflow.calculate_assumptions()
    return assumptions.get('utility_electric', Decimal('0.00'))


def utility_gas(asset_hub_id: int) -> Decimal:
    """
    Get gas utility assumption for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Monthly gas utility cost
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    assumptions = workflow.calculate_assumptions()
    return assumptions.get('utility_gas', Decimal('0.00'))


def utility_water(asset_hub_id: int) -> Decimal:
    """
    Get water utility assumption for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Monthly water utility cost
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    assumptions = workflow.calculate_assumptions()
    return assumptions.get('utility_water', Decimal('0.00'))


def utility_sewer(asset_hub_id: int) -> Decimal:
    """
    Get sewer utility assumption for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Monthly sewer utility cost
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    assumptions = workflow.calculate_assumptions()
    return assumptions.get('utility_sewer', Decimal('0.00'))


def utility_trash(asset_hub_id: int) -> Decimal:
    """
    Get trash utility assumption for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Monthly trash utility cost
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    assumptions = workflow.calculate_assumptions()
    return assumptions.get('utility_trash', Decimal('0.00'))


def utility_other(asset_hub_id: int) -> Decimal:
    """
    Get other utility assumption for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Monthly other utility cost
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    assumptions = workflow.calculate_assumptions()
    return assumptions.get('utility_other', Decimal('0.00'))


def property_management(asset_hub_id: int) -> Decimal:
    """
    Get property management assumption for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Monthly property management cost
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    assumptions = workflow.calculate_assumptions()
    return assumptions.get('property_management', Decimal('0.00'))


def repairs_maintenance(asset_hub_id: int) -> Decimal:
    """
    Get repairs and maintenance assumption for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Monthly repairs and maintenance cost
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    assumptions = workflow.calculate_assumptions()
    return assumptions.get('repairs_maintenance', Decimal('0.00'))


def marketing(asset_hub_id: int) -> Decimal:
    """
    Get marketing assumption for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Monthly marketing cost
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    assumptions = workflow.calculate_assumptions()
    return assumptions.get('marketing', Decimal('0.00'))


def trashout(asset_hub_id: int) -> Decimal:
    """
    Get trashout assumption for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: One-time trashout cost
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    assumptions = workflow.calculate_assumptions()
    return assumptions.get('trashout', Decimal('0.00'))


def renovation(asset_hub_id: int) -> Decimal:
    """
    Get renovation assumption for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: One-time renovation cost
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    assumptions = workflow.calculate_assumptions()
    return assumptions.get('renovation', Decimal('0.00'))


def security_cost(asset_hub_id: int) -> Decimal:
    """
    Get security cost assumption for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Monthly security cost
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    assumptions = workflow.calculate_assumptions()
    return assumptions.get('security_cost', Decimal('0.00'))


def landscaping(asset_hub_id: int) -> Decimal:
    """
    Get landscaping assumption for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Monthly landscaping cost
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    assumptions = workflow.calculate_assumptions()
    return assumptions.get('landscaping', Decimal('0.00'))


def pool_maintenance(asset_hub_id: int) -> Decimal:
    """
    Get pool maintenance assumption for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Decimal: Monthly pool maintenance cost
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    assumptions = workflow.calculate_assumptions()
    return assumptions.get('pool_maintenance', Decimal('0.00'))


def get_all_assumptions(asset_hub_id: int) -> Dict[str, Decimal]:
    """
    Get all utility and property management assumptions for an asset.
    
    Args:
        asset_hub_id: The AssetIdHub primary key
        
    Returns:
        Dict[str, Decimal]: Dictionary containing all calculated costs and metadata
    """
    workflow = UtilityAssumptionWorkflow(asset_hub_id)
    return workflow.calculate_assumptions()
