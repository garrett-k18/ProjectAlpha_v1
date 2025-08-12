from django.db import models
from .seller import SellerRawData


class InternalValuation(models.Model):
    """Model to store internal and third-party valuations linked to a specific SellerRawData instance"""
    # One-to-one relationship with SellerRawData
    seller_raw_data = models.OneToOneField(
        SellerRawData,
        on_delete=models.CASCADE,
        related_name='internal_valuation'
    )
    
    # Internal underwriting values
    internal_uw_asis_value = models.DecimalField(max_digits=15, decimal_places=2)
    internal_uw_arv_value = models.DecimalField(max_digits=15, decimal_places=2)
    internal_uw_value_date = models.DateField()

    # Third-party values
    thirdparty_asis_value = models.DecimalField(max_digits=15, decimal_places=2)
    thirdparty_arv_value = models.DecimalField(max_digits=15, decimal_places=2)
    thirdparty_value_date = models.DateField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Internal Valuation for {self.seller_raw_data.id}"


class BrokerValues(models.Model):
    """Model to store broker valuations linked to a specific SellerRawData instance"""
    # One-to-one relationship with SellerRawData
    seller_raw_data = models.OneToOneField(
        SellerRawData,
        on_delete=models.CASCADE,
        related_name='broker_valuation'
    )
    
    # Broker values
    broker_asis_value = models.DecimalField(max_digits=15, decimal_places=2)
    broker_arv_value = models.DecimalField(max_digits=15, decimal_places=2)
    broker_value_date = models.DateField()
    broker_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Broker Valuation for {self.seller_raw_data.id}"


class BrokerPhoto(models.Model):
    """Model to store broker photos with many-to-one relationship to BrokerValues"""
    # Many-to-one relationship with BrokerValues
    broker_valuation = models.ForeignKey(
        BrokerValues, 
        on_delete=models.CASCADE, 
        related_name='photos'
    )
    
    # Photo fields
    photo = models.ImageField(upload_to=get_broker_photo_path)
    
    # Timestamps
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.photo} photo for {self.broker_valuation.seller_raw_data.id}"
    
    class Meta:
        ordering = ['upload_date']


def get_broker_photo_path(instance, filename):
    """Generates file path for broker photos
    
    Creates path structure: broker_photos/[seller_id]/[trade_id]/[filename]
    """
    # For BrokerPhotos model
    if hasattr(instance, 'broker_valuation'):
        seller_id = instance.broker_valuation.seller_raw_data.seller.id
        trade_id = instance.broker_valuation.seller_raw_data.trade.id
    # For direct photos on BrokerValues model if we add them later
    else:
        seller_id = instance.seller_raw_data.seller.id
        trade_id = instance.seller_raw_data.trade.id
        
    return f'broker_photos/{seller_id}/{trade_id}/{filename}'