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


class CRMContactTag(models.TextChoices):
    BROKER = 'broker', 'Broker'
    TRADING_PARTNER = 'trading_partner', 'Trading Partner'
    INVESTOR = 'investor', 'Investor'
    LEGAL = 'legal', 'Legal'
    VENDOR = 'vendor', 'Vendor'
    SERVICER = 'servicer', 'Servicer'
    TITLE_COMPANY = 'title_company', 'Title Company'


class ValuationType(models.TextChoices):
    """
    Valuation type choices for property valuations.
    
    What this does:
    - Defines valid valuation type values (BPO, Appraisal, AVM)
    - Provides both value (stored in DB) and label (displayed in UI)
    
    How to use:
    - In models: valuation_type = models.CharField(max_length=20, choices=ValuationType.choices)
    - Access value: ValuationType.BPO returns 'bpo'
    - Access label: ValuationType.BPO.label returns 'Broker Price Opinion'
    
    Used by:
    - core.models.Valuation
    """
    BPO = 'bpo', 'Broker Price Opinion'
    APPRAISAL = 'appraisal', 'Appraisal'
    AVM = 'avm', 'Automated Valuation Model'


class BpoType(models.TextChoices):
    """
    BPO/Inspection type choices.
    Also known as: Assignment Type, Report Type
    
    What this does:
    - Defines the type of inspection performed for a BPO
    - Determines access level and detail of the valuation
    
    Used by:
    - core.models.Valuation
    """
    INTERIOR = 'interior', 'Interior Inspection'
    EXTERIOR = 'exterior', 'Exterior Inspection'
    DRIVE_BY = 'drive_by', 'Drive By'
    DESKTOP = 'desktop', 'Desktop/Remote'


class Occupancy(models.TextChoices):
    """
    Property occupancy status choices.
    
    What this does:
    - Defines who currently occupies the property
    - Used for valuation adjustments and marketing strategies
    
    Used by:
    - core.models.Valuation
    - acq_module.models.SellerRawData
    """
    OWNER = 'owner', 'Owner Occupied'
    TENANT = 'tenant', 'Tenant Occupied'
    VACANT = 'vacant', 'Vacant'
    UNKNOWN = 'unknown', 'Unknown'


class PropertyTypeDetail(models.TextChoices):
    """
    Detailed property type choices for valuations.
    More granular than the main PropertyType enum.
    
    What this does:
    - Provides specific property sub-types used in appraisals/BPOs
    - Different from PropertyType which is used for assumptions
    
    Used by:
    - core.models.Valuation
    """
    SF_DETACHED = 'sf_detached', 'Single Family Detached'
    SF_ATTACHED = 'sf_attached', 'Single Family Attached'
    CONDO = 'condo', 'Condominium'
    TOWNHOUSE = 'townhouse', 'Townhouse'
    PUD = 'pud', 'PUD'
    TWO_TO_FOUR_UNIT = '2_4_unit', '2-4 Unit Multi-Family'
    FIVE_PLUS_UNIT = '5plus_unit', '5+ Unit Multi-Family'
    MOBILE = 'mobile', 'Mobile/Manufactured'
    LAND = 'land', 'Land/Vacant'
    COMMERCIAL = 'commercial', 'Commercial'
    MIXED_USE = 'mixed_use', 'Mixed Use'


class Style(models.TextChoices):
    """
    Architectural style choices for properties.
    
    What this does:
    - Defines the architectural style and story configuration
    - Used for comparable selection and adjustments
    
    Used by:
    - core.models.Valuation
    - core.models.Comparable
    """
    SINGLE_STORY = 'single_story', 'Single Story / Ranch'
    ONE_STORY = '1_story', '1 Story'
    ONE_HALF_STORY = '1.5_story', '1.5 Story'
    TWO_STORY = '2_story', '2 Story'
    TWO_STORY_CONV = '2_story_conv', '2 Story Conventional'
    THREE_PLUS_STORY = '3_story', '3+ Story'
    SPLIT_LEVEL = 'split_level', 'Split Level'
    SPLIT_FOYER = 'split_foyer', 'Split Foyer'
    BI_LEVEL = 'bi_level', 'Bi-Level'
    TRI_LEVEL = 'tri_level', 'Tri-Level'
    COLONIAL = 'colonial', 'Colonial'
    CONTEMPORARY = 'contemporary', 'Contemporary'
    CAPE_COD = 'cape_cod', 'Cape Cod'
    BUNGALOW = 'bungalow', 'Bungalow'
    VICTORIAN = 'victorian', 'Victorian'
    TUDOR = 'tudor', 'Tudor'
    MEDITERRANEAN = 'mediterranean', 'Mediterranean'
    OTHER = 'other', 'Other'


class Condition(models.TextChoices):
    """
    Property condition rating choices.
    Supports multiple rating scales: C1-C6, Q1-Q6, and descriptive.
    
    What this does:
    - Standardizes condition ratings across different appraisal formats
    - C1-C6 = Fannie Mae scale
    - Q1-Q6 = Quality rating scale
    - Descriptive = Plain language ratings
    
    Used by:
    - core.models.Valuation
    - core.models.Comparable
    """
    C1 = 'C1', 'C1 - Excellent'
    C2 = 'C2', 'C2 - Very Good'
    C3 = 'C3', 'C3 - Good'
    C4 = 'C4', 'C4 - Average'
    C5 = 'C5', 'C5 - Fair'
    C6 = 'C6', 'C6 - Poor'
    Q1 = 'Q1', 'Q1 - Excellent'
    Q2 = 'Q2', 'Q2 - Very Good'
    Q3 = 'Q3', 'Q3 - Good'
    Q4 = 'Q4', 'Q4 - Average'
    Q5 = 'Q5', 'Q5 - Fair'
    Q6 = 'Q6', 'Q6 - Poor'
    EXCELLENT = 'excellent', 'Excellent'
    VERY_GOOD = 'very_good', 'Very Good'
    GOOD = 'good', 'Good'
    AVERAGE = 'average', 'Average'
    FAIR = 'fair', 'Fair'
    POOR = 'poor', 'Poor'


class View(models.TextChoices):
    """
    Property view type choices.
    
    What this does:
    - Describes what the property overlooks
    - Used for value adjustments and marketing appeal
    
    Used by:
    - core.models.Valuation
    """
    NONE = 'none', 'None/Typical'
    RESIDENTIAL = 'residential', 'Residential'
    RESIDENTIAL_STREET = 'residential_street', 'Residential Street'
    WATER = 'water', 'Water'
    WATERFRONT = 'waterfront', 'Waterfront'
    LAKE = 'lake', 'Lake'
    OCEAN = 'ocean', 'Ocean'
    MOUNTAIN = 'mountain', 'Mountain'
    CITY = 'city', 'City'
    PARK = 'park', 'Park'
    GOLF_COURSE = 'golf_course', 'Golf Course'
    GREENBELT = 'greenbelt', 'Greenbelt'
    PASTORAL = 'pastoral', 'Pastoral'


class Garage(models.TextChoices):
    """
    Garage/parking configuration choices.
    
    What this does:
    - Defines the type and capacity of garage/parking
    - Used for comparable adjustments
    
    Used by:
    - core.models.Valuation
    - core.models.Comparable
    """
    NONE = 'none', 'None'
    CARPORT = 'carport', 'Carport'
    ONE_CAR = '1_car', '1 Car'
    ONE_ATTACHED = '1_attached', '1 Car Attached'
    TWO_ATTACHED = '2_attached', '2 Car Attached'
    THREE_PLUS_ATTACHED = '3_attached', '3+ Car Attached'
    ONE_DETACHED = '1_detached', '1 Car Detached'
    TWO_DETACHED = '2_detached', '2 Car Detached'
    THREE_PLUS_DETACHED = '3_detached', '3+ Car Detached'
    ONE_BUILTIN = '1_builtin', '1 Car Built-in'
    TWO_BUILTIN = '2_builtin', '2 Car Built-in'


class FoundationType(models.TextChoices):
    """
    Foundation type choices.
    
    What this does:
    - Defines the foundation construction type
    - Used for structural assessment and comparables
    
    Used by:
    - core.models.Valuation
    """
    BASEMENT = 'basement', 'Basement'
    FULL_BASEMENT = 'full_basement', 'Full Basement'
    PARTIAL_BASEMENT = 'partial_basement', 'Partial Basement'
    CRAWL_SPACE = 'crawl_space', 'Crawl Space'
    SLAB = 'slab', 'Slab'
    PIER_BEAM = 'pier_beam', 'Pier & Beam'
    NONE = 'none', 'None'
    NA = 'n/a', 'N/A'


class HeatingType(models.TextChoices):
    """
    Heating system type choices.
    Also known as: Heating System, HVAC (heating component)
    
    What this does:
    - Defines the primary heating system type
    - Used for system assessments and energy analysis
    
    Used by:
    - core.models.Valuation
    """
    GAS = 'gas', 'Gas'
    ELECTRIC = 'electric', 'Electric'
    OIL = 'oil', 'Oil'
    FORCED_AIR = 'forced_air', 'Forced Air'
    BASEBOARD = 'baseboard', 'Baseboard'
    RADIANT = 'radiant', 'Radiant'
    HEAT_PUMP = 'heat_pump', 'Heat Pump'
    WOOD = 'wood', 'Wood/Pellet'
    NONE = 'none', 'None'


class CoolingType(models.TextChoices):
    """
    Cooling system type choices.
    Also known as: AC Type, Air Conditioning
    
    What this does:
    - Defines the primary cooling system type
    - Used for system assessments and comfort evaluation
    
    Used by:
    - core.models.Valuation
    """
    CENTRAL = 'central', 'Central AC'
    WALL = 'wall', 'Wall Unit'
    WINDOW = 'window', 'Window Units'
    EVAPORATIVE = 'evaporative', 'Evaporative/Swamp Cooler'
    HEAT_PUMP = 'heat_pump', 'Heat Pump'
    NONE = 'none', 'None'


class WaterType(models.TextChoices):
    """
    Water source type choices.
    
    What this does:
    - Defines the water supply source
    - Used for utility assessments and rural property evaluation
    
    Used by:
    - core.models.Valuation
    """
    PUBLIC = 'public', 'Public'
    WELL = 'well', 'Well'
    SHARED_WELL = 'shared_well', 'Shared Well'
    CISTERN = 'cistern', 'Cistern'


class SewerType(models.TextChoices):
    """
    Sewer/waste system type choices.
    
    What this does:
    - Defines the waste disposal system
    - Used for utility assessments and rural property evaluation
    
    Used by:
    - core.models.Valuation
    """
    PUBLIC = 'public', 'Public Sewer'
    SEPTIC = 'septic', 'Septic'
    CESSPOOL = 'cesspool', 'Cesspool'
    HOLDING_TANK = 'holding_tank', 'Holding Tank'


class MarketingTime(models.TextChoices):
    """
    Typical marketing time choices.
    Also known as: Days on Market ranges, Marketing Period
    
    What this does:
    - Estimates how long it takes to sell similar properties
    - Used for liquidity assessment and market analysis
    
    Used by:
    - core.models.Valuation
    """
    ZERO_TO_THIRTY = '0-30', '0 to 30 Days'
    THIRTY_TO_SIXTY = '30-60', '30 to 60 Days'
    THIRTY_TO_NINETY = '30-90', '30 to 90 Days'
    SIXTY_TO_NINETY = '60-90', '60 to 90 Days'
    NINETY_TO_ONE_TWENTY = '90-120', '90 to 120 Days'
    NINETY_TO_ONE_EIGHTY = '90-180', '90 to 180 Days'
    ONE_EIGHTY_TO_THREE_SIXTY_FIVE = '180-365', '180 to 365 Days'
    OVER_THREE_SIXTY_FIVE = '365+', 'Over 365 Days'


class SalesStrategy(models.TextChoices):
    """
    Sales strategy choices.
    
    What this does:
    - Defines the property's sale condition assumption
    - Used for valuation scenarios and pricing strategy
    
    Used by:
    - core.models.Valuation
    """
    AS_IS = 'as_is', 'As-Is'
    AS_REPAIRED = 'as_repaired', 'As-Repaired'
    QUICK_SALE = 'quick_sale', 'Quick Sale'


class AppraisalPurpose(models.TextChoices):
    """
    Appraisal purpose choices.
    
    What this does:
    - Defines the reason for the appraisal
    - Used for compliance and report formatting
    
    Used by:
    - core.models.Valuation
    """
    PURCHASE = 'purchase', 'Purchase Transaction'
    REFINANCE = 'refinance', 'Refinance'
    EQUITY = 'equity', 'Home Equity/Line of Credit'
    OTHER = 'other', 'Other'


class PropertyRights(models.TextChoices):
    """
    Property rights appraised choices.
    
    What this does:
    - Defines the ownership interest being valued
    - Critical for legal compliance in appraisals
    
    Used by:
    - core.models.Valuation
    """
    FEE_SIMPLE = 'fee_simple', 'Fee Simple'
    LEASEHOLD = 'leasehold', 'Leasehold'
    LEASED_FEE = 'leased_fee', 'Leased Fee'


class LocationType(models.TextChoices):
    """
    Location/neighborhood type choices.
    
    What this does:
    - Defines the general location classification
    - Used for market analysis and comparable selection
    
    Used by:
    - core.models.Valuation
    """
    URBAN = 'urban', 'Urban'
    SUBURBAN = 'suburban', 'Suburban'
    RURAL = 'rural', 'Rural'


class MarketTrend(models.TextChoices):
    """
    Market trend choices.
    
    What this does:
    - Describes the current market direction
    - Used for market conditions analysis
    
    Used by:
    - core.models.Valuation
    """
    STABLE = 'stable', 'Stable'
    DECLINING = 'declining', 'Declining'
    IMPROVING = 'improving', 'Improving'
    UNDER_IMPROVEMENT = 'under_improvement', 'Under Improvement'
    RAPID_GROWTH = 'rapid_growth', 'Rapid Growth'


class Supply(models.TextChoices):
    """
    Market supply level choices.
    
    What this does:
    - Describes the inventory level in the market
    - Used for market conditions analysis
    
    Used by:
    - core.models.Valuation
    """
    SHORTAGE = 'shortage', 'Shortage/Under Supply'
    BALANCED = 'balanced', 'Balanced/In Balance'
    STABLE = 'stable', 'Stable'
    OVERSUPPLY = 'oversupply', 'Over Supply'


class RiskLevel(models.TextChoices):
    """
    Risk level choices.
    
    What this does:
    - General risk assessment scale
    - Used for various risk evaluations
    
    Used by:
    - core.models.Valuation
    """
    LOW = 'low', 'Low'
    MODERATE = 'moderate', 'Moderate'
    HIGH = 'high', 'High'


class Grade(models.TextChoices):
    """
    Academic-style letter grade choices.
    
    What this does:
    - Provides standard A-F letter grade scale
    - Can be used for property ratings, quality assessments, etc.
    
    Used by:
    - Various models requiring letter grade ratings
    """
    A_PLUS = 'A+', 'A+'
    A = 'A', 'A'
    B = 'B', 'B'
    C = 'C', 'C'
    D = 'D', 'D'
    F = 'F', 'F'


class Pride(models.TextChoices):
    """
    Pride of ownership / Quality maintenance choices.
    
    What this does:
    - Assesses how well the neighborhood is maintained
    - Used for neighborhood quality evaluation
    
    Used by:
    - core.models.Valuation
    """
    EXCELLENT = 'excellent', 'Excellent'
    GOOD = 'good', 'Good'
    AVERAGE = 'average', 'Average'
    FAIR = 'fair', 'Fair'
    POOR = 'poor', 'Poor'


class SubjectAppeal(models.TextChoices):
    """
    Subject property appeal choices.
    Compared to average homes in the area.
    
    What this does:
    - Rates the subject property's appeal relative to neighborhood
    - Used for marketability assessment
    
    Used by:
    - core.models.Valuation
    """
    SUPERIOR = 'superior', 'Superior'
    ABOVE_AVERAGE = 'above_average', 'Above Average'
    AVERAGE = 'average', 'Average'
    BELOW_AVERAGE = 'below_average', 'Below Average'
    UNDER_IMPROVEMENT = 'under_improvement', 'Under Improvement'
    LOW = 'low', 'Low'


class OwnershipType(models.TextChoices):
    """
    Ownership type choices.
    
    What this does:
    - Defines how the property is owned/used
    - Used for occupancy analysis
    
    Used by:
    - core.models.Valuation
    """
    HOMEOWNER = 'homeowner', 'Homeowner'
    OWNER_OCCUPANT = 'owner_occupant', 'Owner Occupant'
    INVESTOR = 'investor', 'Investor'
    RENTAL = 'rental', 'Rental'


class CompType(models.TextChoices):
    """
    Comparable sale type choices.
    
    What this does:
    - Defines the status of the comparable sale
    - Used for weighting and reliability assessment
    
    Used by:
    - core.models.Comparable
    """
    SOLD = 'sold', 'Closed Sale'
    LISTING = 'listing', 'Active Listing'
    PENDING = 'pending', 'Pending Sale'
    EXPIRED = 'expired', 'Expired Listing'
    WITHDRAWN = 'withdrawn', 'Withdrawn Listing'


class SalesType(models.TextChoices):
    """
    Sales/Transaction type choices.
    Also known as: Type of Sale/Listing, Transaction Type
    
    What this does:
    - Defines the nature of the transaction
    - Critical for determining if sale is arms-length and valid for comps
    
    Used by:
    - core.models.Comparable
    """
    RETAIL = 'retail', 'Retail'
    ARMS_LENGTH = 'arms_length', 'Arms Length / Fair Market'
    FAIR_MARKET = 'fair_market', 'Fair Market'
    REO = 'reo', 'REO/Bank Owned'
    SHORT_SALE = 'short_sale', 'Short Sale'
    FORECLOSURE = 'foreclosure', 'Foreclosure'
    ESTATE_SALE = 'estate_sale', 'Estate Sale'
    RELOCATION = 'relocation', 'Relocation'
    NON_ARMS_LENGTH = 'non_arms_length', 'Non-Arms Length'
    UNKNOWN = 'unknown', 'Unknown'


class FinancingType(models.TextChoices):
    """
    Financing type choices.
    
    What this does:
    - Defines how the sale was financed
    - Used for market analysis and financing adjustments
    
    Used by:
    - core.models.Comparable
    """
    CASH = 'cash', 'Cash'
    CONVENTIONAL = 'conventional', 'Conventional'
    FHA = 'fha', 'FHA'
    VA = 'va', 'VA'
    USDA = 'usda', 'USDA'
    SELLER_FINANCING = 'seller_financing', 'Seller Financing'
    OTHER = 'other', 'Other'
    UNKNOWN = 'unknown', 'Unknown'


class CompRanking(models.IntegerChoices):
    """
    Comparable ranking choices.
    Note: Uses IntegerChoices instead of TextChoices for numeric values.
    
    What this does:
    - Ranks the quality/relevance of comparables
    - Used for weighting in valuation analysis
    
    Used by:
    - core.models.Comparable
    """
    BEST = 1, '1 - Best'
    SECOND = 2, '2'
    WORST = 3, '3 - Worst'


class RepairCategory(models.TextChoices):
    """
    Repair category choices.
    Comprehensive list of repair types for BPO repair estimates.
    
    What this does:
    - Categorizes repairs by location and type
    - Used for organizing repair line items
    
    Used by:
    - core.models.RepairItem
    """
    # Interior repairs
    PAINT_INT = 'paint_int', 'Paint (Interior)'
    WALLS_CEILING = 'walls_ceiling', 'Walls/Ceiling'
    FLOORING = 'flooring', 'Flooring/Carpet'
    KITCHEN = 'kitchen', 'Kitchen'
    CABINETS_COUNTERTOPS = 'cabinets_countertops', 'Cabinets/Countertops'
    BATHROOMS = 'bathrooms', 'Bathrooms'
    PLUMBING = 'plumbing', 'Plumbing'
    ELECTRICAL = 'electrical', 'Electrical'
    HVAC = 'hvac', 'Heating/Cooling/HVAC'
    APPLIANCES = 'appliances', 'Appliances'
    DOORS_TRIM_INT = 'doors_trim_int', 'Doors/Trim (Interior)'
    STAIRS = 'stairs', 'Stairs/Railings'
    BASEMENT = 'basement', 'Basement'
    CLEANING = 'cleaning', 'Cleaning/Debris Removal'
    OTHER_INTERNAL = 'other_internal', 'Other (Internal)'
    
    # Exterior repairs
    ROOF = 'roof', 'Roof'
    SIDING = 'siding', 'Siding'
    TRIM = 'trim', 'Trim/Soffit/Fascia'
    STRUCTURAL = 'structural', 'Structural'
    WINDOWS = 'windows', 'Windows'
    DOORS_EXT = 'doors_ext', 'Doors (Exterior)'
    PAINT_EXT = 'paint_ext', 'Paint (Exterior)'
    POWER_WASH = 'power_wash', 'Power Wash'
    FOUNDATION = 'foundation', 'Foundation'
    GARAGE = 'garage', 'Garage'
    DRIVEWAY = 'driveway', 'Driveway'
    WALKWAY = 'walkway', 'Walkway/Sidewalk'
    LANDSCAPING = 'landscaping', 'Landscaping'
    TREES_REMOVAL = 'trees_removal', 'Tree Removal/Trimming'
    FENCE = 'fence', 'Fence/Gate'
    DECK_PATIO = 'deck_patio', 'Deck/Patio'
    POOL = 'pool', 'Pool/Spa'
    GUTTERS = 'gutters', 'Gutters/Downspouts'
    GRADING_DRAINAGE = 'grading_drainage', 'Grading/Drainage'
    OTHER_EXTERNAL = 'other_external', 'Other (External)'
    
    # Systems
    SEPTIC = 'septic', 'Septic System'
    WELL = 'well', 'Well'
    OTHER_SYSTEMS = 'other_systems', 'Other Systems'


class RepairType(models.TextChoices):
    """
    Repair location type choices.
    High-level grouping of repair categories.
    
    What this does:
    - Groups repairs by internal/external/systems
    - Used for summary reporting and filtering
    
    Used by:
    - core.models.RepairItem
    """
    INTERNAL = 'internal', 'Internal'
    EXTERNAL = 'external', 'External'
    SYSTEMS = 'systems', 'Systems'


class Severity(models.TextChoices):
    """
    Repair severity level choices.
    
    What this does:
    - Rates the urgency/importance of repairs
    - Used for prioritization and risk assessment
    
    Used by:
    - core.models.RepairItem
    """
    COSMETIC = 'cosmetic', 'Cosmetic'
    MINOR = 'minor', 'Minor'
    MODERATE = 'moderate', 'Moderate'
    MAJOR = 'major', 'Major'
    CRITICAL = 'critical', 'Critical/Safety'


class PhotoType(models.TextChoices):
    """
    Photo type choices for valuation photos.
    Comprehensive categorization of valuation-related photos.
    
    What this does:
    - Categorizes photos by subject and purpose
    - Used for organizing and displaying valuation photos
    
    Used by:
    - core.models.ValuationPhoto
    """
    # Subject property exterior
    FRONT = 'front', 'Front View'
    REAR = 'rear', 'Rear View'
    LEFT_SIDE = 'left_side', 'Left Side View'
    RIGHT_SIDE = 'right_side', 'Right Side View'
    STREET = 'street', 'Street Scene'
    STREET_LEFT = 'street_left', 'Street Left View'
    STREET_RIGHT = 'street_right', 'Street Right View'
    STREET_SIGN = 'street_sign', 'Street Sign'
    ADDRESS_VERIFICATION = 'address_verification', 'Address Verification'
    ADDRESS_CLOSEUP = 'address_closeup', 'Address Closeup'
    MAILBOX = 'mailbox', 'Mailbox'
    
    # Interior rooms
    KITCHEN = 'kitchen', 'Kitchen'
    LIVING_ROOM = 'living_room', 'Living Room'
    DINING_ROOM = 'dining_room', 'Dining Room'
    BEDROOM = 'bedroom', 'Bedroom'
    BATHROOM = 'bathroom', 'Bathroom'
    BASEMENT = 'basement', 'Basement'
    INTERIOR_OTHER = 'interior_other', 'Interior Other'
    
    # Property features
    GARAGE = 'garage', 'Garage'
    POOL = 'pool', 'Pool'
    DECK_PATIO = 'deck_patio', 'Deck/Patio'
    LANDSCAPING = 'landscaping', 'Landscaping'
    
    # Condition/repairs
    DAMAGE = 'damage', 'Damage'
    REPAIR_NEEDED = 'repair_needed', 'Repair Needed'
    
    # Comparable properties
    COMP_SALE_1 = 'comp_sale_1', 'Comparable Sale #1'
    COMP_SALE_2 = 'comp_sale_2', 'Comparable Sale #2'
    COMP_SALE_3 = 'comp_sale_3', 'Comparable Sale #3'
    COMP_SALE_4 = 'comp_sale_4', 'Comparable Sale #4'
    COMP_LIST_1 = 'comp_list_1', 'Comparable Listing #1'
    COMP_LIST_2 = 'comp_list_2', 'Comparable Listing #2'
    COMP_LIST_3 = 'comp_list_3', 'Comparable Listing #3'
    
    # Documentation
    MAP = 'map', 'Map/Location'
    FLOOD_MAP = 'flood_map', 'Flood Map'
    PUBLIC_RECORDS = 'public_records', 'Public Records'
    ASSESSMENT = 'assessment', 'Assessment Record'
    OTHER = 'other', 'Other'


class NoteTag(models.TextChoices):
    """
    Tag categories for AM notes.
    
    What this does:
    - Provides standardized tags for categorizing asset management notes
    - Used for filtering and organizing notes in the UI
    
    Used by:
    - am_module.models.AMNote
    """
    GENERAL = 'general', 'General'
    LEGAL = 'legal', 'Legal'
    ESCROW = 'escrow', 'Escrow'
    FORECLOSURE = 'foreclosure', 'Foreclosure'
    REO = 'reo', 'REO'
    BORROWER_HEIR = 'borrower_heir', 'Borrower/Heir'


class YesNo(models.TextChoices):
    """
    Yes/No choices for boolean fields that need string values.
    Note: Use BooleanField for true boolean logic. This is for display/forms.
    
    What this does:
    - Provides Yes/No text choices instead of True/False
    - Used when you need string representation of boolean values
    
    Used by:
    - Various models where text-based boolean is needed
    """
    YES = 'yes', 'Yes'
    NO = 'no', 'No'

