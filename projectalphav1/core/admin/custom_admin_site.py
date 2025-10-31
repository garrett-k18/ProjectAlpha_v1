"""
DEPRECATED: This file is no longer used.

We've reverted to using standard Django admin instead of django-admin-groups.
All admin registrations are now in core/admin.py using standard Django admin.
This file can be safely deleted.
"""

from django.contrib import admin
from django.contrib.admin.apps import AdminConfig


class CustomAdminSite(admin.AdminSite):
    """
    Custom admin site with improved model organization.
    
    This customizes the admin site to group models visually.
    """
    site_header = "ProjectAlpha Administration"
    site_title = "ProjectAlpha Admin"
    index_title = "Welcome to ProjectAlpha Administration"
    
    def get_app_list(self, request):
        """
        Customize app list to group models into logical sections.
        
        Returns a structured list of apps with their models organized
        into logical groups for better navigation.
        """
        # Get the default app list from Django
        app_list = super().get_app_list(request)
        
        # Group models by logical categories
        # This creates visual grouping in the admin interface
        organized_apps = []
        
        # Define module groupings
        module_groups = {
            'Core - Assets': ['core'],
            'Core - Capital Management': ['core'],  # Filtered by model names
            'Core - CRM': ['core'],
            'Core - Assumptions': ['core'],
            'Acquisition Module': ['acq_module'],
            'Asset Management Module': ['am_module'],
            'Reporting': ['reporting'],
            'User Management': ['user_admin'],
        }
        
        # Process each app and organize models
        for app_dict in app_list:
            app_label = app_dict['app_label']
            
            # Group models by logical categories
            if app_label == 'core':
                # Split core models into logical groups
                capital_models = [
                    m for m in app_dict['models']
                    if m['name'] in ['DebtFacility', 'CoInvestor', 'InvestorContribution', 
                                    'InvestorDistribution', 'Fund']
                ]
                crm_models = [
                    m for m in app_dict['models']
                    if m['name'] in ['MasterCRM']
                ]
                assumptions_models = [
                    m for m in app_dict['models']
                    if m['name'] in ['Servicer', 'StateReference', 'FCStatus', 
                                    'FCTimelines', 'CommercialUnits', 'HOAAssumption']
                ]
                assets_models = [
                    m for m in app_dict['models']
                    if m['name'] not in ['DebtFacility', 'CoInvestor', 'InvestorContribution',
                                        'InvestorDistribution', 'Fund', 'MasterCRM',
                                        'Servicer', 'StateReference', 'FCStatus',
                                        'FCTimelines', 'CommercialUnits', 'HOAAssumption']
                ]
                
                # Create separate app entries for each group
                if capital_models:
                    organized_apps.append({
                        'name': 'Core - Capital Management',
                        'app_label': 'core_capital',
                        'models': capital_models,
                    })
                if crm_models:
                    organized_apps.append({
                        'name': 'Core - CRM',
                        'app_label': 'core_crm',
                        'models': crm_models,
                    })
                if assumptions_models:
                    organized_apps.append({
                        'name': 'Core - Assumptions',
                        'app_label': 'core_assumptions',
                        'models': assumptions_models,
                    })
                if assets_models:
                    organized_apps.append({
                        'name': 'Core - Assets',
                        'app_label': 'core_assets',
                        'models': assets_models,
                    })
            else:
                # Keep other apps as-is
                organized_apps.append(app_dict)
        
        return organized_apps


# Create a custom admin site instance
custom_admin_site = CustomAdminSite(name='admin')


class CustomAdminConfig(AdminConfig):
    """Custom admin config that uses our custom admin site."""
    default_site = 'core.admin.custom_admin_site.CustomAdminSite'

