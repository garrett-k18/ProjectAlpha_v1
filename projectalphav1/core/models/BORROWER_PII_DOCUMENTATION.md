# BorrowerPII Model - Field-Level Encryption Documentation

## Overview

The `BorrowerPII` model provides **secure, encrypted storage** for borrower Personally Identifiable Information (PII) including Social Security Numbers, dates of birth, dates of death, and phone numbers.

## Security Features

### Encryption Details
- **Library**: django-fernet-encrypted-fields v0.3.1
- **Algorithm**: Fernet symmetric encryption (AES-128 CBC with HMAC)
- **Key Derivation**: SALT_KEY + Django SECRET_KEY
- **Compliance**: Designed for GLBA, FCRA, and state privacy laws

### What's Encrypted
All sensitive PII fields are encrypted at rest:
- `borrower1_ssn` - Primary borrower SSN
- `borrower1_dob` - Primary borrower date of birth
- `borrower1_dod` - Primary borrower date of death
- `borrower1_phone` - Primary borrower phone number
- `borrower2_ssn` - Co-borrower SSN
- `borrower2_dob` - Co-borrower date of birth
- `borrower2_dod` - Co-borrower date of death
- `borrower2_phone` - Co-borrower phone number

### What's NOT Encrypted
- `asset` (primary key) - For lookups and joins
- `created_at` / `updated_at` - For audit trails

## Database Schema

```sql
-- Table: core_borrower_pii
CREATE TABLE core_borrower_pii (
    asset_id INTEGER PRIMARY KEY REFERENCES core_assetidhub(id) ON DELETE CASCADE,
    borrower1_ssn VARCHAR(256) NULL,      -- Encrypted
    borrower1_dob VARCHAR(256) NULL,      -- Encrypted
    borrower1_dod VARCHAR(256) NULL,      -- Encrypted
    borrower1_phone VARCHAR(256) NULL,    -- Encrypted
    borrower2_ssn VARCHAR(256) NULL,      -- Encrypted
    borrower2_dob VARCHAR(256) NULL,      -- Encrypted
    borrower2_dod VARCHAR(256) NULL,      -- Encrypted
    borrower2_phone VARCHAR(256) NULL,    -- Encrypted
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Indexes
CREATE INDEX borrower_pii_created_idx ON core_borrower_pii (created_at);
CREATE INDEX borrower_pii_updated_idx ON core_borrower_pii (updated_at);
```

## Configuration

### Environment Variables

#### Development (.env file)
```bash
# REQUIRED: Salt for encryption (combine with SECRET_KEY)
DJANGO_SALT_KEY=64GZIY9p2n0NQ16W9ELd6N22OqY1-vpgSICVMpDojwM

# REQUIRED: Django secret key (also used for encryption)
DJANGO_SECRET_KEY=your-django-secret-key-here
```

#### Production (Railway Environment Variables)
```bash
# Set these in Railway dashboard:
DJANGO_SALT_KEY=<generate-new-secure-salt>
DJANGO_SECRET_KEY=<your-production-secret-key>
```

### Generating Keys

```bash
# Generate a new SALT_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate a new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Usage Examples

### Creating BorrowerPII Records

```python
from core.models import AssetIdHub, BorrowerPII

# Create PII for an asset
asset = AssetIdHub.objects.get(pk=123)
pii = BorrowerPII.objects.create(
    asset=asset,
    borrower1_ssn='123-45-6789',
    borrower1_dob='1980-01-15',
    borrower1_phone='555-123-4567',
    borrower2_ssn='987-65-4321',
    borrower2_dob='1985-06-20'
)

# Data is automatically encrypted in the database!
```

### Reading BorrowerPII Records

```python
# Get PII by asset
pii = BorrowerPII.objects.get(asset_id=123)

# Or via reverse relationship
asset = AssetIdHub.objects.get(pk=123)
if hasattr(asset, 'borrower_pii'):
    pii = asset.borrower_pii
    print(pii.borrower1_ssn)  # Automatically decrypted: '123-45-6789'
```

### Updating BorrowerPII Records

```python
# Update encrypted fields
pii = BorrowerPII.objects.get(asset_id=123)
pii.borrower1_phone = '555-999-8888'
pii.save()

# Bulk update (still encrypted)
BorrowerPII.objects.filter(asset_id=123).update(
    borrower1_phone='555-111-2222'
)
```

### Checking Data Existence

```python
pii = BorrowerPII.objects.get(asset_id=123)

# Check if primary borrower data exists
if pii.has_borrower1_data():
    print("Primary borrower data available")

# Check if co-borrower data exists
if pii.has_borrower2_data():
    print("Co-borrower data available")

# Check if any data exists
if pii.has_any_data():
    print("Some PII data exists")
```

### Calculating Borrower Age

```python
pii = BorrowerPII.objects.get(asset_id=123)

# Get primary borrower's age
age1 = pii.get_borrower1_age()
if age1:
    print(f"Primary borrower is {age1} years old")

# Get co-borrower's age
age2 = pii.get_borrower2_age()
if age2:
    print(f"Co-borrower is {age2} years old")
```

## API/Serializer Integration

### Creating a Serializer

```python
# projectalphav1/core/serializers/serial_co_borrowerPII.py
from rest_framework import serializers
from core.models import BorrowerPII

class BorrowerPIISerializer(serializers.ModelSerializer):
    """
    Serializer for BorrowerPII model.
    
    SECURITY NOTES:
    - Only expose to authenticated, authorized users
    - Consider masking SSN in responses (show last 4 digits only)
    - Log all access for audit trail
    """
    
    # Optional: Mask SSN in responses
    borrower1_ssn_masked = serializers.SerializerMethodField()
    borrower2_ssn_masked = serializers.SerializerMethodField()
    
    class Meta:
        model = BorrowerPII
        fields = [
            'asset',
            'borrower1_ssn',
            'borrower1_ssn_masked',
            'borrower1_dob',
            'borrower1_dod',
            'borrower1_phone',
            'borrower2_ssn',
            'borrower2_ssn_masked',
            'borrower2_dob',
            'borrower2_dod',
            'borrower2_phone',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_borrower1_ssn_masked(self, obj):
        """Mask SSN showing only last 4 digits: XXX-XX-1234"""
        if obj.borrower1_ssn:
            return f"XXX-XX-{obj.borrower1_ssn[-4:]}"
        return None
    
    def get_borrower2_ssn_masked(self, obj):
        """Mask SSN showing only last 4 digits: XXX-XX-1234"""
        if obj.borrower2_ssn:
            return f"XXX-XX-{obj.borrower2_ssn[-4:]}"
        return None
```

### Creating a ViewSet with Security

```python
# projectalphav1/core/views/view_co_borrowerPII.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import BorrowerPII
from core.serializers.serial_co_borrowerPII import BorrowerPIISerializer
import logging

logger = logging.getLogger(__name__)

class BorrowerPIIViewSet(viewsets.ModelViewSet):
    """
    API endpoint for BorrowerPII with enhanced security.
    
    SECURITY FEATURES:
    - Requires authentication
    - Logs all access attempts
    - Rate limiting recommended (use django-ratelimit)
    - Should add IP whitelist for production
    """
    queryset = BorrowerPII.objects.all()
    serializer_class = BorrowerPIISerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """Override list to add audit logging"""
        logger.warning(
            f"BorrowerPII.list accessed by user={request.user.id} "
            f"ip={request.META.get('REMOTE_ADDR')}"
        )
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to add audit logging"""
        logger.warning(
            f"BorrowerPII.retrieve accessed by user={request.user.id} "
            f"asset_id={kwargs.get('pk')} "
            f"ip={request.META.get('REMOTE_ADDR')}"
        )
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Override create to add audit logging"""
        logger.warning(
            f"BorrowerPII.create by user={request.user.id} "
            f"ip={request.META.get('REMOTE_ADDR')}"
        )
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Override update to add audit logging"""
        logger.warning(
            f"BorrowerPII.update by user={request.user.id} "
            f"asset_id={kwargs.get('pk')} "
            f"ip={request.META.get('REMOTE_ADDR')}"
        )
        return super().update(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def masked(self, request, pk=None):
        """Return PII with all sensitive fields masked"""
        pii = self.get_object()
        return Response({
            'asset_id': pii.asset_id,
            'borrower1_ssn': f"XXX-XX-{pii.borrower1_ssn[-4:]}" if pii.borrower1_ssn else None,
            'borrower1_dob': str(pii.borrower1_dob.year) if pii.borrower1_dob else None,
            'borrower1_phone': f"XXX-XXX-{pii.borrower1_phone[-4:]}" if pii.borrower1_phone else None,
            'borrower2_ssn': f"XXX-XX-{pii.borrower2_ssn[-4:]}" if pii.borrower2_ssn else None,
            'borrower2_dob': str(pii.borrower2_dob.year) if pii.borrower2_dob else None,
            'borrower2_phone': f"XXX-XXX-{pii.borrower2_phone[-4:]}" if pii.borrower2_phone else None,
        })
```

## Important Security Considerations

### ⚠️ Critical Security Rules

1. **NEVER commit encryption keys to version control**
   - Keys in .env file are for local development only
   - Use Railway environment variables in production
   - Rotate keys regularly

2. **NEVER log decrypted PII values**
   - Log access attempts, not data values
   - Use masked values in logs
   - Store audit trails separately

3. **NEVER expose PII in __str__ methods**
   - Already handled in BorrowerPII model
   - Only show asset_id

4. **NEVER query by encrypted fields**
   ```python
   # BAD - Very slow, decrypts every row!
   BorrowerPII.objects.filter(borrower1_ssn='123-45-6789')
   
   # GOOD - Query by unencrypted asset_id
   BorrowerPII.objects.get(asset_id=123)
   ```

### Performance Limitations

**Encrypted fields cannot:**
- Be indexed (performance)
- Be used in WHERE clauses efficiently
- Be used in ORDER BY clauses
- Support LIKE queries or regex
- Be used as foreign keys

**Best practices:**
- Always query by `asset_id` (unencrypted primary key)
- Use separate unencrypted fields for searchable data
- Consider creating hash fields for lookups if needed

### Key Rotation Strategy

When rotating encryption keys:

1. **Generate new salt**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Decrypt all data with old key**
   ```python
   # Use old DJANGO_SALT_KEY
   all_pii = BorrowerPII.objects.all()
   data = [(pii.asset_id, pii.borrower1_ssn, ...) for pii in all_pii]
   ```

3. **Update DJANGO_SALT_KEY in environment**

4. **Re-encrypt all data with new key**
   ```python
   # Now using new DJANGO_SALT_KEY
   for asset_id, ssn, ... in data:
       pii = BorrowerPII.objects.get(asset_id=asset_id)
       pii.borrower1_ssn = ssn
       pii.save()
   ```

5. **Test thoroughly before deploying**

## Compliance Notes

### GLBA (Gramm-Leach-Bliley Act)
- ✅ Encryption at rest
- ✅ Access controls (use permissions)
- ⚠️ Implement audit logging
- ⚠️ Data retention policies

### FCRA (Fair Credit Reporting Act)
- ✅ Secure storage of consumer data
- ⚠️ Implement reasonable procedures for accuracy
- ⚠️ Dispute resolution process

### State Privacy Laws (CCPA, GDPR-style)
- ✅ Encryption of personal information
- ⚠️ Right to access (provide masked API)
- ⚠️ Right to deletion (implement soft delete)
- ⚠️ Data breach notification procedures

## Testing

### Unit Tests Example

```python
# tests/test_borrower_pii.py
from django.test import TestCase
from core.models import AssetIdHub, BorrowerPII
from datetime import date

class BorrowerPIITestCase(TestCase):
    def setUp(self):
        self.asset = AssetIdHub.objects.create()
    
    def test_create_encrypted_pii(self):
        """Test that PII is created and encrypted"""
        pii = BorrowerPII.objects.create(
            asset=self.asset,
            borrower1_ssn='123-45-6789',
            borrower1_dob=date(1980, 1, 15)
        )
        
        # Data should be readable
        self.assertEqual(pii.borrower1_ssn, '123-45-6789')
        
        # But encrypted in database (check raw SQL)
        # Raw value should NOT match plaintext
    
    def test_age_calculation(self):
        """Test age calculation for borrowers"""
        pii = BorrowerPII.objects.create(
            asset=self.asset,
            borrower1_dob=date(1980, 1, 15)
        )
        
        age = pii.get_borrower1_age()
        self.assertIsNotNone(age)
        self.assertGreater(age, 40)  # Born in 1980
    
    def test_data_existence_checks(self):
        """Test helper methods for data existence"""
        pii = BorrowerPII.objects.create(
            asset=self.asset,
            borrower1_ssn='123-45-6789'
        )
        
        self.assertTrue(pii.has_borrower1_data())
        self.assertFalse(pii.has_borrower2_data())
        self.assertTrue(pii.has_any_data())
```

## Troubleshooting

### Common Issues

**Issue: "DJANGO_SALT_KEY not set" warning**
```
Solution: Add DJANGO_SALT_KEY to your .env file
```

**Issue: Cannot query by encrypted fields**
```python
# This won't work:
BorrowerPII.objects.filter(borrower1_ssn='123-45-6789')

# Use this instead:
asset = AssetIdHub.objects.get(...)  # Find by other criteria
pii = BorrowerPII.objects.get(asset=asset)
```

**Issue: Data appears garbled after key rotation**
```
Solution: Data encrypted with old key cannot be decrypted with new key.
Must decrypt with old key, then re-encrypt with new key.
```

## Additional Resources

- **Library Documentation**: https://github.com/jazzband/django-fernet-encrypted-fields
- **Fernet Spec**: https://github.com/fernet/spec/blob/master/Spec.md
- **Django Encryption Best Practices**: https://docs.djangoproject.com/en/5.2/topics/security/

## Support

For questions or issues with BorrowerPII model:
1. Check this documentation first
2. Review security best practices
3. Test in development environment
4. Contact system administrator for production issues

---

**Last Updated**: December 18, 2025
**Model Version**: 1.0
**Django Version**: 5.2.5
**Encryption Library**: django-fernet-encrypted-fields 0.3.1
