from acq_module.models.seller import SellerRawData

# Get distinct occupancy values
occupancy_values = SellerRawData.objects.values_list('occupancy', flat=True).distinct()
print("Distinct occupancy values in database:")
for val in occupancy_values:
    count = SellerRawData.objects.filter(occupancy=val).count()
    print(f"  '{val}': {count} records")
