"""
Database router to handle schema routing for different models
"""

class SchemaRouter:
    """
    Routes database operations to the appropriate schema:
    - Models from seller.py go to 'seller_data' schema
    - All other models go to 'core' schema
    """
    
    # Define which models belong to which schema
    SELLER_MODELS = {
        'acq_module.models.seller.Seller',
        'acq_module.models.seller.Trade',
        'acq_module.models.seller.AcqAsset',
        'acq_module.models.seller.AcqLoan',
        'acq_module.models.seller.AcqProperty',
        'acq_module.models.seller.AcqForeclosureTimeline',
    }
    
    def _is_seller_model(self, model):
        """Check if a model belongs to the seller schema"""
        model_path = f"{model.__module__}.{model.__name__}"
        return model_path in self.SELLER_MODELS
    
    def db_for_read(self, model, **hints):
        """
        Reads from the appropriate schema based on the model
        """
        if self._is_seller_model(model):
            return 'seller_data'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """
        Writes to the appropriate schema based on the model
        """
        if self._is_seller_model(model):
            return 'seller_data'
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations between objects if they're in compatible schemas
        """
        obj1_db = 'seller_data' if self._is_seller_model(obj1.__class__) else 'default'
        obj2_db = 'seller_data' if self._is_seller_model(obj2.__class__) else 'default'
        
        # Allow relations within the same database
        if obj1_db == obj2_db:
            return True
            
        # Allow cross-schema relations for foreign keys
        # (Django can handle these with proper configuration)
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure that migrations run on the appropriate schema
        """
        # Get the model if available
        model = hints.get('model')
        
        if db == 'seller_data':
            # Only allow seller models in seller_data schema
            if model:
                return self._is_seller_model(model)
            # For migrations without model hints, check by name
            if model_name and app_label == 'acq_module':
                seller_model_names = [
                    'seller',
                    'trade',
                    'acqasset',
                    'acqloan',
                    'acqproperty',
                    'acqforeclosuretimeline',
                ]
                return model_name.lower() in seller_model_names
            return False
            
        elif db == 'default':
            # Don't allow seller models in default schema
            if model:
                return not self._is_seller_model(model)
            # For migrations without model hints, check by name  
            if model_name and app_label == 'acq_module':
                seller_model_names = [
                    'seller',
                    'trade',
                    'acqasset',
                    'acqloan',
                    'acqproperty',
                    'acqforeclosuretimeline',
                ]
                return model_name.lower() not in seller_model_names
            return True
            
        return False