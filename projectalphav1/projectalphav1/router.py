"""
Database router to handle schema routing for different models
"""

class SchemaRouter:
    """
    Routes database operations to the appropriate schema:
    - Models from seller.py go to 'seller_data' schema
    - All other models go to 'core' schema
    """
    
    def db_for_read(self, model, **hints):
        """
        Reads from the appropriate schema based on the model's module path
        """
        # Check if this is from the seller models
        if model.__module__ == 'acq_module.models.seller':
            return 'seller_data'
        return 'default'  # Use 'default' which points to core schema
    
    def db_for_write(self, model, **hints):
        """
        Writes to the appropriate schema based on the model's module path
        """
        if model.__module__ == 'acq_module.models.seller':
            return 'seller_data'
        return 'default'  # Use 'default' which points to core schema
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations between objects if they're in the same database
        or if at least one is in the core schema.
        """
        # If either object is in the core schema, allow the relation
        obj1_schema = 'seller_data' if obj1.__class__.__module__ == 'acq_module.models.seller' else 'default'
        obj2_schema = 'seller_data' if obj2.__class__.__module__ == 'acq_module.models.seller' else 'default'
        
        if obj1_schema == obj2_schema:
            return True
        return True  # Allow cross-schema relations (typically what you want)
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure that the migrations only run on the appropriate schema
        """
        # For explicit migrations to a specific database
        if db == 'seller_data':
            # When explicitly migrating to seller_data, only allow seller models
            if 'model' in hints:
                return hints['model'].__module__ == 'acq_module.models.seller'
            # For initial migrations without model hints
            if model_name:
                # Check if this is a seller model by name (case-insensitive)
                seller_models = ['seller', 'trade', 'sellerrawdata']
                return model_name.lower() in seller_models
            # For app migrations without model name
            if app_label == 'acq_module':
                # Allow acq_module migrations on seller_data for initial setup
                return True
            return False
            
        # For default database
        if db == 'default':
            # When explicitly migrating to default, don't allow seller models
            if 'model' in hints:
                return hints['model'].__module__ != 'acq_module.models.seller'
            # For initial migrations without model hints
            if model_name:
                # Check if this is a seller model by name
                seller_models = ['seller', 'trade', 'sellerrawdata']
                return model_name.lower() not in seller_models
            return True
            
        # For other databases
        return False
