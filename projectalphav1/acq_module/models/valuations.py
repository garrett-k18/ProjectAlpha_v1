from django.db import models
from .seller import SellerRawData
import os
from datetime import datetime

# Function to determine the upload path for broker photos
def get_broker_photo_path(instance, filename):
    """Generate a file path for storing broker photos
    
    Args:
        instance: The BrokerPhoto instance being saved
        filename: Original filename of the uploaded photo
        
    Returns:
        str: Path where the file will be stored
    """
    # Get the broker valuation ID and related seller raw data ID
    broker_id = instance.broker_valuation.id
    seller_id = instance.broker_valuation.seller_raw_data.id
    
    # Format the filename with timestamp to avoid collisions
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}{ext}"
    
    # Return the path: broker_photos/seller_id/broker_id/filename
    return os.path.join('broker_photos', str(seller_id), str(broker_id), new_filename)


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
    
    class Meta:
        verbose_name = "Internal Valuation"
        verbose_name_plural = "Internal Valuations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller_raw_data']),
        ]
        db_table = 'acq_internal_valuation'
    
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
    
    class Meta:
        verbose_name = "Broker Values"
        verbose_name_plural = "Broker Values"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller_raw_data']),
        ]
        db_table = 'acq_broker_values'
    
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
    
    class Meta:
        verbose_name = "Broker Photo"
        verbose_name_plural = "Broker Photos"
        ordering = ['upload_date']
        indexes = [
            models.Index(fields=['broker_valuation']),
        ]
        db_table = 'acq_broker_photo'
    
    def __str__(self):
        return f"{self.photo} photo for {self.broker_valuation.seller_raw_data.id}"


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