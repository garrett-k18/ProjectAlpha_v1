# ProjectAlpha_v1 Database Model Structure

**Purpose**: Complete documentation of all Django models for creating interconnected test data using Factory Boy and Faker.

**Date Created**: 2026-01-29

---

## Table of Contents
1. [Core Models (Hub & Central Data)](#core-models)
2. [Acquisition Module Models](#acquisition-module-models)
3. [Asset Management Module Models](#asset-management-module-models)
4. [Capital Structure Models](#capital-structure-models)
5. [CRM & Contact Models](#crm--contact-models)
6. [Assumptions & Configuration Models](#assumptions--configuration-models)
7. [Valuation Models](#valuation-models)
8. [Geographic Reference Models](#geographic-reference-models)
9. [General Ledger & Financial Models](#general-ledger--financial-models)
10. [ETL & Import Models](#etl--import-models)
11. [Model Relationship Summary](#model-relationship-summary)

---

## Core Models

### AssetIdHub
**Location**: `core/models/model_co_assetIdHub.py`
**Purpose**: Central hub providing stable integer ID for assets across all modules
**Table**: `core_assetidhub`

**Fields**:
- `id` (PK, AutoField) - Primary key
- `sellertape_id` (CharField, indexed) - External seller tape key
- `servicer_id` (CharField, indexed) - External servicer ID
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Relationships**:
- **1:1 with SellerRawData** (via `acq_raw`)
- **1:1 with AssetDetails** (via `details`)
- **1:1 with LlDataEnrichment** (via `enrichment`)
- **1:1 with LLTransactionSummary** (via `ll_transaction_summary`)
- **1:Many with Valuation** (via `valuations`)
- **1:Many with ComparableProperty** (via `comparable_properties`)
- **1:Many with GeneralLedgerEntries** (via `gl_entries`)
- **1:Many with LLCashFlowSeries** (via `ll_cash_flow_series`)
- **1:Many with LoanLevelAssumption** (via `loan_assumptions`)
- **1:Many with AMMetrics** (via `ammetrics`)
- **1:Many with AMNote** (via `am_notes`)
- **1:Many with AssetCRMContact** (via `crm_contacts`)
- **1:1 with REOData** (via `reo_data`)
- **1:1 with FCSale** (via `fc_sale`)
- **1:1 with DIL** (via `dil`)
- **1:1 with ShortSale** (via `short_sale`)
- **1:1 with Modification** (via `modification`)
- **1:1 with NoteSale** (via `note_sale`)

### AssetDetails
**Location**: `core/models/model_co_assetIdHub.py`
**Purpose**: Minimal asset details linking hub to fund/legal entity
**Table**: `asset_details`

**Fields**:
- `asset` (OneToOneField to AssetIdHub, PK) - Primary key
- `fund_legal_entity` (FK to FundLegalEntity, nullable)
- `trade` (FK to Trade, nullable)
- `is_commercial` (BooleanField, nullable)
- `asset_status` (CharField) - Choices: ACTIVE, LIQUIDATED
- `legacy_flag` (BooleanField, indexed, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

---

## Acquisition Module Models

### Seller
**Location**: `acq_module/models/model_acq_seller.py`
**Purpose**: Represents sellers/trading partners
**Table**: `acq_seller`

**Fields**:
- `id` (PK, AutoField)
- `name` (CharField, indexed)
- `broker` (CharField, nullable)
- `email` (EmailField, nullable)
- `poc` (CharField, nullable) - Point of contact

**Relationships**:
- **1:Many with Trade** (via `trades`)
- **1:Many with SellerRawData** (via `seller_raw_data`)

### Trade
**Location**: `acq_module/models/model_acq_seller.py`
**Purpose**: Represents individual trade deals
**Table**: `acq_trade`

**Fields**:
- `id` (PK, AutoField)
- `seller` (FK to Seller)
- `trade_name` (CharField)
- `status` (CharField, indexed) - Choices: PASS, INDICATIVE, DD, AWARDED, BOARD
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Relationships**:
- **Many:1 with Seller** (via `seller`)
- **1:Many with SellerRawData** (via `seller_raw_data`)
- **1:Many with TradeLevelAssumption** (via `trade_assumptions`)
- **1:Many with AssetDetails** (via `asset_details`)

### SellerRawData
**Location**: `acq_module/models/model_acq_seller.py`
**Purpose**: Raw acquisition data from seller tapes
**Table**: `acq_sellerrawdata`

**Fields**:
- `asset_hub` (OneToOneField to AssetIdHub, PK) - Primary key
- `seller` (FK to Seller, nullable)
- `trade` (FK to Trade, nullable)
- `sellertape_id` (CharField, max 100)
- `sellertape_altid` (CharField, max 100, nullable)
- `asset_status` (CharField) - Choices: NPL, REO, PERF, RPL
- `acq_status` (CharField, indexed) - Choices: KEEP, DROP
- `as_of_date` (DateField, nullable)
- `street_address` (CharField, nullable)
- `city` (CharField, nullable)
- `state` (CharField, nullable)
- `zip` (CharField, nullable)
- `property_type` (CharField) - Uses PropertyType choices
- `product_type` (CharField) - Choices: BPL, HECM, VA, Conv, Commercial
- `occupancy` (CharField) - Choices: Vacant, Occupied, Unknown
- `year_built` (IntegerField, nullable)
- `sq_ft` (IntegerField, nullable)
- `lot_size` (IntegerField, nullable)
- `beds` (IntegerField, nullable)
- `baths` (IntegerField, nullable)
- `borrower1_last` (CharField, nullable)
- `borrower1_first` (CharField, nullable)
- `borrower2_last` (CharField, nullable)
- `borrower2_first` (CharField, nullable)
- `current_balance` (DecimalField, nullable)
- `deferred_balance` (DecimalField, nullable)
- `interest_rate` (DecimalField, nullable)
- `next_due_date` (DateField, nullable)
- `last_paid_date` (DateField, nullable)
- `first_pay_date` (DateField, nullable)
- `origination_date` (DateField, nullable)
- `original_balance` (DecimalField, nullable)
- `original_term` (IntegerField, nullable)
- `original_rate` (DecimalField, nullable)
- `original_maturity_date` (DateField, nullable)
- `default_rate` (DecimalField, nullable)
- `months_dlq` (IntegerField, nullable)
- `current_maturity_date` (DateField, nullable)
- `current_term` (IntegerField, nullable)
- `accrued_note_interest` (DecimalField, nullable)
- `accrued_default_interest` (DecimalField, nullable)
- `escrow_balance` (DecimalField, nullable)
- `escrow_advance` (DecimalField, nullable)
- `recoverable_corp_advance` (DecimalField, nullable)
- `late_fees` (DecimalField, nullable)
- `other_fees` (DecimalField, nullable)
- `suspense_balance` (DecimalField, nullable)
- `total_debt` (DecimalField, nullable)
- `origination_value` (DecimalField, nullable)
- `origination_arv` (DecimalField, nullable)
- `origination_value_date` (DateField, nullable)
- `seller_value_date` (DateField, nullable)
- `seller_arv_value` (DecimalField, nullable)
- `seller_asis_value` (DecimalField, nullable)
- `additional_asis_value` (DecimalField, nullable)
- `additional_arv_value` (DecimalField, nullable)
- `additional_value_date` (DateField, nullable)
- `fc_flag` (BooleanField, nullable)
- `fc_first_legal_date` (DateField, nullable)
- `fc_referred_date` (DateField, nullable)
- `fc_judgement_date` (DateField, nullable)
- `fc_scheduled_sale_date` (DateField, nullable)
- `fc_sale_date` (DateField, nullable)
- `fc_starting` (DecimalField, nullable)
- `bk_flag` (BooleanField, nullable)
- `bk_chapter` (CharField, nullable)
- `mod_flag` (BooleanField)
- `mod_date` (DateField, nullable)
- `mod_maturity_date` (DateField, nullable)
- `mod_term` (IntegerField, nullable)
- `mod_rate` (DecimalField, nullable)
- `mod_initial_balance` (DecimalField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

---

## Asset Management Module Models

### AMMetrics
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: Asset management metrics and status tracking
**Table**: `am_ammetrics`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub, nullable)
- `delinquency_status` (CharField) - Choices: current, 30, 60, 90, 120_plus
- `final_proceeds` (DecimalField, nullable)
- `proceeds_source` (CharField, nullable) - Choices: reo, short_sale, foreclosure, dil, modification, note_sale, other
- `proceeds_date` (DateField, nullable)
- `updated_at` (DateTimeField, auto_now)
- `updated_by` (FK to User, nullable)

### AMNote
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: User notes attached to assets
**Table**: `am_note`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub, nullable)
- `body` (TextField)
- `tag` (CharField, nullable) - Choices: urgent, legal, qc, ops, info
- `scope` (CharField) - Choices: asset, outcome, task
- `context_outcome` (CharField, nullable) - Choices: dil, fc, reo, short_sale, modification, note_sale
- `context_task_type` (CharField, nullable)
- `context_task_id` (IntegerField, nullable)
- `pinned` (BooleanField)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)
- `created_by` (FK to User, nullable)
- `updated_by` (FK to User, nullable)

### AssetCRMContact
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: Junction model linking assets to CRM contacts
**Table**: `am_asset_crm_contact`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub)
- `crm` (FK to MasterCRM)
- `role` (CharField, indexed, nullable) - e.g., 'legal', 'servicer', 'broker'
- `notes` (TextField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Unique Together**: `['asset_hub', 'crm', 'role']`

### REOData
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: REO property disposition data
**Table**: `am_reodata`

**Fields**:
- `asset_hub` (OneToOneField to AssetIdHub, PK)
- `list_price` (DecimalField, nullable)
- `list_date` (DateField, nullable)
- `under_contract_flag` (BooleanField)
- `under_contract_date` (DateField, nullable)
- `contract_price` (DecimalField, nullable)
- `estimated_close_date` (DateField, nullable)
- `actual_close_date` (DateField, nullable)
- `seller_credit_amt` (DecimalField, nullable)
- `purchase_type` (CharField, nullable) - Choices: cash, financing, seller_financing
- `gross_purchase_price` (DecimalField, nullable)

### REOtask
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: REO workflow tasks
**Table**: `am_reotask`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub)
- `reo_outcome` (FK to REOData)
- `task_type` (CharField) - Choices: eviction, trashout, renovation, marketing, under_contract, sold
- `task_started` (DateField, default today)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Unique Together**: `['asset_hub', 'task_type']`

### FCSale
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: Foreclosure sale data
**Table**: `am_fcsale`

**Fields**:
- `asset_hub` (OneToOneField to AssetIdHub, PK)
- `nod_noi_sent_date` (DateField, nullable)
- `nod_noi_expire_date` (DateField, nullable)
- `fc_sale_sched_date` (DateField, nullable)
- `fc_sale_actual_date` (DateField, nullable)
- `fc_bid_price` (DecimalField, nullable)
- `fc_sale_price` (DecimalField, nullable)

### FCTask
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: Foreclosure workflow tasks
**Table**: `am_fctask`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub)
- `fc_sale` (FK to FCSale)
- `task_type` (CharField) - Choices: nod_noi, fc_filing, mediation, judgement, redemption, sale_scheduled, sold
- `task_started` (DateField, default today)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Unique Together**: `['asset_hub', 'task_type']`

### DIL
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: Deed in Lieu data
**Table**: `am_dil`

**Fields**:
- `asset_hub` (OneToOneField to AssetIdHub, PK)
- `dil_completion_date` (DateField, nullable)
- `dil_cost` (DecimalField, nullable)
- `cfk_cost` (DecimalField, nullable)

### DILTask
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: DIL workflow tasks
**Table**: `am_diltask`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub)
- `dil` (FK to DIL)
- `task_type` (CharField) - Choices: pursuing_dil, owner_contacted, dil_failed, dil_drafted, dil_executed
- `task_started` (DateField, default today)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Unique Together**: `['asset_hub', 'task_type']`

### ShortSale
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: Short sale data
**Table**: `am_shortsale`

**Fields**:
- `asset_hub` (OneToOneField to AssetIdHub, PK)
- `acceptable_min_offer` (DecimalField, nullable)
- `short_sale_date` (DateField, nullable)
- `gross_proceeds` (DecimalField, nullable)
- `short_sale_list_date` (DateField, nullable)
- `short_sale_list_price` (DecimalField, nullable)

### ShortSaleTask
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: Short sale workflow tasks
**Table**: `am_shortsaletask`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub)
- `short_sale` (FK to ShortSale)
- `task_type` (CharField) - Choices: list_price_accepted, listed, under_contract, sold
- `task_started` (DateField, default today)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Unique Together**: `['asset_hub', 'task_type']`

### Modification
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: Loan modification data
**Table**: `am_modification`

**Fields**:
- `asset_hub` (OneToOneField to AssetIdHub, PK)
- `modification_date` (DateField, nullable)
- `modification_cost` (DecimalField, nullable)
- `modification_upb` (DecimalField, nullable)
- `modification_term` (IntegerField, nullable)
- `modification_rate` (DecimalField, nullable)
- `modification_maturity_date` (DateField, nullable)
- `modification_pi` (CharField, nullable) - Choices: pi, io, other
- `modification_down_payment` (DecimalField, nullable)
- `note_sale_proceeds` (DecimalField, nullable)
- `note_sale_date` (DateField, nullable)

### ModificationTask
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: Modification workflow tasks
**Table**: `am_modificationtask`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub)
- `modification` (FK to Modification)
- `task_type` (CharField) - Choices: mod_drafted, mod_executed, mod_rpl, mod_failed, note_sale
- `task_started` (DateField, default today)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Unique Together**: `['asset_hub', 'task_type']`

### NoteSale
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: Note sale outcome data
**Table**: `am_notesale`

**Fields**:
- `asset_hub` (OneToOneField to AssetIdHub, PK)
- `sold_date` (DateField, default today, nullable)
- `proceeds` (DecimalField, nullable)
- `trading_partner` (FK to MasterCRM, nullable)

### NoteSaleTask
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: Note sale workflow tasks
**Table**: `am_notesaletask`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub)
- `note_sale` (FK to NoteSale)
- `task_type` (CharField) - Choices: potential_note_sale, out_to_market, pending_sale, sold
- `task_started` (DateField, default today, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Unique Together**: `['asset_hub', 'task_type']`

### REOScope
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: Work orders/scopes/bids for properties
**Table**: `am_reoscope`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub)
- `crm` (FK to MasterCRM, nullable) - Vendor/contractor
- `scope_kind` (CharField, nullable) - Choices: trashout, renovation
- `reo_task` (FK to REOtask, nullable)
- `scope_date` (DateField, nullable)
- `total_cost` (DecimalField, nullable)
- `expected_completion` (DateField, nullable)
- `notes` (TextField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### Offers
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: Track offers for properties
**Table**: `am_offers`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub)
- `offer_source` (CharField) - Choices: short_sale, reo, note_sale
- `offer_price` (DecimalField)
- `offer_date` (DateField, nullable)
- `seller_credits` (DecimalField, nullable, default 0)
- `financing_type` (CharField, nullable) - Choices: cash, conventional, fha, va, usda, hard_money, other
- `buyer_name` (CharField, nullable)
- `buyer_agent` (CharField, nullable)
- `trading_partner` (FK to MasterCRM, nullable)
- `offer_status` (CharField) - Choices: pending, under_review, countered, accepted, rejected, withdrawn, expired
- `expiration_date` (DateField, nullable)
- `closing_date` (DateField, nullable)
- `earnest_money` (DecimalField, nullable)
- `inspection_period_days` (PositiveIntegerField, nullable)
- `financing_contingency_days` (PositiveIntegerField, nullable)
- `appraisal_contingency` (BooleanField, default True)
- `special_terms` (TextField, nullable)
- `internal_notes` (TextField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)
- `created_by` (CharField, nullable)

---

## Capital Structure Models

### DebtFacility
**Location**: `core/models/model_co_capStack.py`
**Purpose**: Debt facility information
**Table**: `debt_facility`

**Fields**:
- `id` (PK, AutoField)
- `facility_name` (CharField, nullable)
- `firm_name` (CharField, nullable)
- `firm_email` (EmailField, nullable)
- `firm_phone` (CharField, nullable)
- `commitment_size` (DecimalField, nullable)
- `rate_index` (CharField, default "SOFR", nullable)
- `sofr_rate` (DecimalField, nullable)
- `spread_bps` (PositiveIntegerField, nullable)
- `start_date` (DateField, nullable)
- `end_date` (DateField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### CoInvestor
**Location**: `core/models/model_co_capStack.py`
**Purpose**: Co-investor tracking
**Table**: `co_investor`

**Fields**:
- `id` (PK, AutoField)
- `crm_contact` (FK to MasterCRM, nullable)
- `commitment_amount` (DecimalField, nullable)
- `ownership_percentage` (DecimalField, nullable)
- `is_active` (BooleanField, default True)
- `notes` (TextField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Relationships**:
- **1:Many with InvestorContribution** (via `contributions`)
- **1:Many with InvestorDistribution** (via `distributions`)

### InvestorContribution
**Location**: `core/models/model_co_capStack.py`
**Purpose**: Individual contribution transactions
**Table**: `investor_contribution`

**Fields**:
- `id` (PK, AutoField)
- `co_investor` (FK to CoInvestor)
- `contribution_date` (DateField)
- `amount` (DecimalField)
- `payment_method` (CharField, nullable)
- `reference_number` (CharField, nullable)
- `notes` (TextField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### InvestorDistribution
**Location**: `core/models/model_co_capStack.py`
**Purpose**: Individual distribution transactions
**Table**: `investor_distribution`

**Fields**:
- `id` (PK, AutoField)
- `co_investor` (FK to CoInvestor)
- `distribution_date` (DateField)
- `amount` (DecimalField)
- `distribution_type` (CharField) - Choices: return_of_capital, profit_distribution, preferred_return, promote, other
- `payment_method` (CharField, nullable)
- `reference_number` (CharField, nullable)
- `notes` (TextField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### Entity
**Location**: `core/models/model_co_capStack.py`
**Purpose**: Universal entity model (individuals, LLCs, trusts, etc.)
**Table**: `entity`

**Fields**:
- `id` (PK, AutoField)
- `name` (CharField)
- `entity_type` (CharField) - Choices: fund, individual, llc, jv, corporation, partnership, spv, trust, other
- `tax_id` (CharField, nullable)
- `email` (EmailField)
- `phone` (CharField)
- `is_active` (BooleanField, default True)
- `notes` (TextField)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Relationships**:
- **1:Many with FundLegalEntity** (via `legal_entities`)
- **1:Many with FundMembership** (via `memberships` and `fund_memberships`)
- **1:Many with EntityMembership** (via `child_members` and `parent_memberships`)

### FundLegalEntity
**Location**: `core/models/model_co_capStack.py`
**Purpose**: Legal entities that make up fund structure
**Table**: `fund_legal_entity`

**Fields**:
- `id` (PK, AutoField)
- `fund` (FK to Entity)
- `nickname_name` (CharField, nullable)
- `entity_role` (CharField, nullable) - Choices: fund, gp, lp, spv, jv, co_investor, other
- `jurisdiction` (CharField, nullable)
- `tax_id` (CharField, nullable)
- `is_active` (BooleanField, default True)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Relationships**:
- **1:Many with AssetDetails** (via `asset_assignments`)
- **1:Many with FundMembership** (via `members`)

### FundMembership
**Location**: `core/models/model_co_capStack.py`
**Purpose**: Entity membership in funds (GP/LP tracking)
**Table**: `fund_membership`

**Fields**:
- `id` (PK, AutoField)
- `fund` (FK to Entity)
- `entity` (FK to Entity)
- `member_type` (CharField) - Choices: gp, lp, co_investor, spv, other
- `admission_date` (DateField)
- `ownership_percentage` (DecimalField)
- `capital_committed` (DecimalField, default 0)
- `capital_contributed` (DecimalField, default 0)
- `investing_through` (FK to FundLegalEntity, nullable)
- `is_active` (BooleanField, default True)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Unique Together**: `['fund', 'entity']`

### EntityMembership
**Location**: `core/models/model_co_capStack.py`
**Purpose**: Nested ownership within entities
**Table**: `entity_membership`

**Fields**:
- `id` (PK, AutoField)
- `parent_entity` (FK to Entity)
- `member_entity` (FK to Entity)
- `ownership_percentage` (DecimalField)
- `membership_date` (DateField)
- `capital_account` (DecimalField, default 0)
- `distribution_percentage` (DecimalField, nullable)
- `is_active` (BooleanField, default True)
- `notes` (TextField)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Unique Together**: `['parent_entity', 'member_entity']`

---

## CRM & Contact Models

### FirmCRM
**Location**: `core/models/model_co_crm.py`
**Purpose**: Firm/company CRM records
**Table**: `core_firmcrm`

**Fields**:
- `id` (PK, AutoField)
- `name` (CharField, indexed)
- `phone` (CharField, unique, nullable)
- `email` (EmailField, nullable)
- `tag` (CharField, indexed, nullable) - Uses CRMContactTag choices
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Relationships**:
- **Many:Many with StateReference** (via `states`)
- **1:Many with MasterCRM** (via `contacts`)

### MasterCRM
**Location**: `core/models/model_co_crm.py`
**Purpose**: Unified master CRM directory
**Table**: `core_mastercrm`

**Fields**:
- `id` (PK, AutoField)
- `firm_ref` (FK to FirmCRM, nullable)
- `contact_name` (CharField, nullable)
- `city` (CharField, nullable)
- `email` (EmailField, indexed, nullable)
- `phone` (CharField, nullable)
- `preferred` (CharField, indexed, nullable) - Choices: yes, no
- `tag` (CharField, indexed, nullable) - Choices: broker, trading_partner, investor, legal, vendor, servicer, title_company
- `alt_contact_name` (CharField, nullable)
- `alt_contact_email` (EmailField, nullable)
- `alt_contact_phone` (CharField, nullable)
- `nda_flag` (BooleanField, default False)
- `nda_signed` (DateField, nullable)
- `notes` (TextField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Relationships**:
- **Many:Many with StateReference** (via `states`)
- **Many:Many with MSAReference** (via `msas` through BrokerMSAAssignment)
- **1:Many with Valuation** (via `valuations`)
- **1:Many with CoInvestor** (via `co_investor_records`)
- **1:Many with AssetCRMContact** (via `asset_links`)
- **1:Many with REOScope** (via `reo_scopes`)
- **1:Many with NoteSale** (via `note_sales`)
- **1:Many with Offers** (via `note_sale_offers`)

### BrokerMSAAssignment
**Location**: `core/models/model_co_crm.py`
**Purpose**: Junction table for broker-MSA relationships
**Table**: `broker_msa_assignments`

**Fields**:
- `id` (PK, AutoField)
- `broker` (FK to MasterCRM)
- `msa` (FK to MSAReference, nullable)
- `priority` (IntegerField, default 1)
- `is_active` (BooleanField, default True)
- `notes` (TextField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Unique Together**: `['broker', 'msa']`

---

## Assumptions & Configuration Models

### Servicer
**Location**: `core/models/model_co_assumptions.py`
**Purpose**: Servicer information and fee schedules
**Table**: `servicers`

**Fields**:
- `id` (PK, AutoField)
- `servicer_name` (CharField, unique, indexed)
- `contact_name` (CharField, nullable)
- `contact_email` (EmailField, nullable)
- `contact_phone` (CharField, nullable)
- `servicing_transfer_duration` (IntegerField, nullable)
- `board_fee` (DecimalField, nullable)
- `current_fee` (DecimalField, nullable)
- `thirtday_fee` (DecimalField, nullable)
- `sixtyday_fee` (DecimalField, nullable)
- `ninetyday_fee` (DecimalField, nullable)
- `onetwentyday_fee` (DecimalField, nullable)
- `fc_fee` (DecimalField, nullable)
- `bk_fee` (DecimalField, nullable)
- `mod_fee` (DecimalField, nullable)
- `dil_fee` (DecimalField, nullable)
- `thirdparty_fee` (DecimalField, nullable)
- `reo_fee` (DecimalField, nullable)
- `reo_days` (IntegerField, nullable)
- `liqfee_pct` (DecimalField, nullable)
- `liqfee_flat` (DecimalField, nullable)
- `is_default_for_trade_assumptions` (BooleanField, default False)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Relationships**:
- **1:Many with TradeLevelAssumption** (via `trade_level_assumptions`)

### LoanLevelAssumption
**Location**: `acq_module/models/model_acq_assumptions.py`
**Purpose**: Individual loan-level assumptions
**Table**: `loan_level_assumptions`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub)
- `months_to_resolution` (IntegerField, nullable)
- `probability_of_cure` (DecimalField, nullable)
- `probability_of_foreclosure` (DecimalField, nullable)
- `recovery_percentage` (DecimalField, nullable)
- `monthly_carrying_cost` (DecimalField, nullable)
- `legal_costs` (DecimalField, nullable)
- `foreclosure_costs` (DecimalField, nullable)
- `property_preservation_cost` (DecimalField, nullable)
- `estimated_reo_months` (IntegerField, nullable, default 0)
- `estimated_rehab_cost` (DecimalField, nullable, default 0)
- `estimated_resale_value` (DecimalField, nullable)
- `fc_duration_override_months` (IntegerField, nullable)
- `reo_fc_duration_override_months` (IntegerField, nullable)
- `reo_renovation_override_months` (IntegerField, nullable)
- `reo_marketing_override_months` (IntegerField, nullable)
- `acquisition_price` (DecimalField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### TradeLevelAssumption
**Location**: `acq_module/models/model_acq_assumptions.py`
**Purpose**: Trade-specific assumptions
**Table**: `trade_level_assumptions`

**Fields**:
- `id` (PK, AutoField)
- `trade` (FK to Trade)
- `servicer` (FK to Servicer, nullable, default 1)
- `bid_date` (DateField, nullable)
- `settlement_date` (DateField, nullable)
- `servicing_transfer_date` (DateField, nullable)
- `bid_method` (CharField, nullable) - Choices: PCT_UPB, TARGET_IRR
- `pctUPB` (DecimalField, nullable, default 85.00)
- `target_irr` (DecimalField, nullable)
- `discount_rate` (DecimalField, nullable, default 0.12)
- `wacc` (DecimalField, nullable)
- `total_discount` (DecimalField, nullable)
- `perf_rpl_hold_period` (IntegerField, nullable, default 12)
- `mod_rate` (DecimalField, nullable, default 0.0400)
- `mod_legal_term` (IntegerField, nullable, default 360)
- `mod_amort_term` (IntegerField, nullable, default 360)
- `max_mod_ltv` (DecimalField, nullable, default 0.95)
- `mod_io_flag` (BooleanField, nullable, default False)
- `mod_down_pmt` (DecimalField, nullable, default 0.05)
- `mod_orig_cost` (DecimalField, nullable, default 500.00)
- `mod_setup_duration` (IntegerField, nullable, default 6)
- `mod_hold_duration` (IntegerField, nullable, default 6)
- `acq_legal_cost` (DecimalField, nullable, default 300.00)
- `acq_dd_cost` (DecimalField, nullable, default 150.00)
- `acq_tax_title_cost` (DecimalField, nullable, default 100.00)
- `acq_broker_fees` (DecimalField, nullable, default 0.00)
- `acq_other_costs` (DecimalField, nullable, default 0.00)
- `liq_am_fee_pct` (DecimalField, nullable, default 0.01)
- `liq_broker_cc_pct` (DecimalField, nullable, default 0.01)
- `liq_tax_transfer_cost` (DecimalField, nullable, default 0.00)
- `liq_title_cost` (DecimalField, nullable, default 0.00)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### ModelingDefaults
**Location**: `acq_module/models/model_acq_assumptions.py`
**Purpose**: Global modeling defaults for new trades
**Table**: `acq_modeling_defaults`

**Fields**:
- `id` (PK, AutoField, fixed at 1)
- `default_pct_upb` (DecimalField, nullable)
- `default_discount_rate` (DecimalField, nullable)
- `default_perf_rpl_hold_period` (IntegerField, nullable)
- `default_mod_rate` (DecimalField, nullable)
- `default_mod_legal_term` (IntegerField, nullable)
- `default_mod_amort_term` (IntegerField, nullable)
- `default_max_mod_ltv` (DecimalField, nullable)
- `default_mod_io_flag` (BooleanField, default False)
- `default_mod_down_pmt` (DecimalField, nullable)
- `default_mod_orig_cost` (DecimalField, nullable)
- `default_mod_setup_duration` (IntegerField, nullable)
- `default_mod_hold_duration` (IntegerField, nullable)
- `default_acq_legal_cost` (DecimalField, nullable)
- `default_acq_dd_cost` (DecimalField, nullable)
- `default_acq_tax_title_cost` (DecimalField, nullable)
- `default_am_fee_pct` (DecimalField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### NoteSaleAssumption
**Location**: `acq_module/models/model_acq_assumptions.py`
**Purpose**: Note sale discount factors
**Table**: `note_sale_assumptions`

**Fields**:
- `id` (PK, AutoField)
- `factor_type` (CharField) - Choices: BALANCE, MATURITY, FICO, LTV, PROPERTY_TYPE
- `factor_name` (CharField)
- `index_order` (IntegerField, default 1)
- `range_min` (DecimalField, nullable)
- `range_max` (DecimalField, nullable)
- `range_value` (CharField, nullable)
- `discount_factor` (DecimalField, default 1.0000)
- `priority` (IntegerField, default 0)
- `notes` (TextField, nullable)
- `is_active` (BooleanField, default True)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### FCStatus
**Location**: `core/models/model_co_assumptions.py`
**Purpose**: Foreclosure status categories
**Table**: `fc_status`

**Fields**:
- `id` (PK, AutoField)
- `status` (CharField) - Choices: pre_fc, first_legal_filed, mediation, order_of_reference, judgement, pre_sale_redemption, sale_scheduled, sale_completed, post_sale_redemption
- `order` (IntegerField, default 0)
- `notes` (TextField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### FCTimelines
**Location**: `core/models/model_co_assumptions.py`
**Purpose**: State-specific foreclosure timelines
**Table**: `fc_timelines`

**Fields**:
- `id` (PK, AutoField)
- `state` (FK to StateReference)
- `fc_status` (FK to FCStatus)
- `duration_days` (IntegerField, nullable)
- `cost_avg` (DecimalField, nullable)
- `notes` (TextField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Unique Together**: `['state', 'fc_status']`

### CommercialUnits
**Location**: `core/models/model_co_assumptions.py`
**Purpose**: Commercial property unit-based scaling factors
**Table**: `commercial_units`

**Fields**:
- `id` (PK, AutoField)
- `units` (IntegerField, unique, indexed)
- `fc_cost_scale` (DecimalField, default 1.00)
- `rehab_cost_scale` (DecimalField, default 1.00)
- `rehab_duration_scale` (DecimalField, default 1.00)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### HOAAssumption
**Location**: `core/models/model_co_assumptions.py`
**Purpose**: HOA fee assumptions by property type
**Table**: `hoa_assumptions`

**Fields**:
- `id` (PK, AutoField)
- `property_type` (CharField, unique, indexed) - Uses PropertyType choices
- `monthly_hoa_fee` (DecimalField)
- `notes` (TextField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### PropertyTypeAssumption
**Location**: `core/models/model_co_assumptions.py`
**Purpose**: Property type-based cost assumptions
**Table**: `property_type_assumptions`

**Fields**:
- `id` (PK, AutoField)
- `property_type` (CharField, unique, indexed) - Uses PropertyType choices
- `utility_electric_monthly` (DecimalField, nullable, default None)
- `utility_gas_monthly` (DecimalField, nullable, default None)
- `utility_water_monthly` (DecimalField, nullable, default None)
- `utility_sewer_monthly` (DecimalField, nullable, default None)
- `utility_trash_monthly` (DecimalField, nullable, default None)
- `utility_other_monthly` (DecimalField, nullable, default None)
- `property_management_monthly` (DecimalField, nullable, default None)
- `repairs_maintenance_monthly` (DecimalField, nullable, default None)
- `marketing_monthly` (DecimalField, nullable, default None)
- `trashout_cost` (DecimalField, nullable, default None)
- `renovation_cost` (DecimalField, nullable, default None)
- `security_cost_monthly` (DecimalField, nullable, default None)
- `landscaping_monthly` (DecimalField, nullable, default None)
- `pool_maintenance_monthly` (DecimalField, nullable, default None)
- `notes` (TextField, nullable)
- `is_active` (BooleanField, default True, indexed)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### SquareFootageAssumption
**Location**: `core/models/model_co_assumptions.py`
**Purpose**: Square footage-based cost assumptions
**Table**: `square_footage_assumptions`

**Fields**:
- `id` (PK, AutoField)
- `property_category` (CharField, indexed) - Choices: RESIDENTIAL, COMMERCIAL
- `description` (CharField)
- `utility_electric_per_sqft` (DecimalField, nullable)
- `utility_gas_per_sqft` (DecimalField, nullable)
- `utility_water_per_sqft` (DecimalField, nullable)
- `utility_sewer_per_sqft` (DecimalField, nullable)
- `utility_trash_per_sqft` (DecimalField, nullable)
- `utility_other_per_sqft` (DecimalField, nullable)
- `property_management_per_sqft` (DecimalField, nullable)
- `repairs_maintenance_per_sqft` (DecimalField, nullable)
- `marketing_per_sqft` (DecimalField, nullable)
- `security_cost_per_sqft` (DecimalField, nullable)
- `landscaping_per_sqft` (DecimalField, nullable)
- `pool_maintenance_per_sqft` (DecimalField, nullable)
- `trashout_per_sqft` (DecimalField, nullable)
- `renovation_per_sqft` (DecimalField, nullable)
- `notes` (TextField, nullable)
- `is_active` (BooleanField, default True, indexed)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Unique Together**: `['property_category', 'description']`

### UnitBasedAssumption
**Location**: `core/models/model_co_assumptions.py`
**Purpose**: Unit-based assumptions for multifamily
**Table**: `unit_based_assumptions`

**Fields**:
- `id` (PK, AutoField)
- `units_min` (IntegerField, indexed)
- `units_max` (IntegerField, indexed, nullable)
- `utility_electric_per_unit` (DecimalField, default 0)
- `utility_gas_per_unit` (DecimalField, default 0)
- `utility_water_per_unit` (DecimalField, default 0)
- `utility_sewer_per_unit` (DecimalField, default 0)
- `utility_trash_per_unit` (DecimalField, default 0)
- `utility_other_per_unit` (DecimalField, default 0)
- `property_management_per_unit` (DecimalField, default 0)
- `repairs_maintenance_per_unit` (DecimalField, default 0)
- `marketing_per_unit` (DecimalField, default 0)
- `security_cost_per_unit` (DecimalField, default 0)
- `landscaping_per_unit` (DecimalField, default 0)
- `pool_maintenance_per_unit` (DecimalField, default 0)
- `trashout_per_unit` (DecimalField, default 0)
- `renovation_per_unit` (DecimalField, default 0)
- `description` (CharField)
- `notes` (TextField, nullable)
- `is_active` (BooleanField, default True, indexed)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

---

## Valuation Models

### ValuationGradeReference
**Location**: `core/models/model_co_valuations.py`
**Purpose**: Reference table for valuation grades
**Table**: `core_valuation_grade_reference`

**Fields**:
- `id` (PK, AutoField)
- `code` (CharField, unique, indexed) - Uses Grade choices (A+, A, B, C, D, F)
- `label` (CharField)
- `description` (TextField, nullable)
- `sort_order` (PositiveIntegerField, default 0, indexed)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### Valuation
**Location**: `core/models/model_co_valuations.py`
**Purpose**: Property valuations from various sources
**Table**: `acq_valuations`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub, indexed)
- `broker_contact` (FK to MasterCRM, indexed, nullable)
- `grade` (FK to ValuationGradeReference, indexed, nullable)
- `source` (CharField, indexed) - Choices: internalInitialUW, internal, broker, desktop, BPOI, BPOE, seller, appraisal
- `asis_value` (DecimalField, nullable)
- `arv_value` (DecimalField, nullable)
- `value_date` (DateField, indexed, nullable)
- `trashout_est_total` (DecimalField, nullable)
- `rehab_est_total` (DecimalField, nullable)
- `recommend_rehab` (BooleanField, default False)
- `recommend_rehab_reason` (TextField, nullable)
- `roof_est` (DecimalField, nullable)
- `roof_grade` (CharField, nullable) - Uses Grade choices
- `kitchen_est` (DecimalField, nullable)
- `kitchen_grade` (CharField, nullable) - Uses Grade choices
- `bath_est` (DecimalField, nullable)
- `bath_grade` (CharField, nullable) - Uses Grade choices
- `flooring_est` (DecimalField, nullable)
- `flooring_grade` (CharField, nullable) - Uses Grade choices
- `windows_est` (DecimalField, nullable)
- `windows_grade` (CharField, nullable) - Uses Grade choices
- `appliances_est` (DecimalField, nullable)
- `appliances_grade` (CharField, nullable) - Uses Grade choices
- `plumbing_est` (DecimalField, nullable)
- `plumbing_grade` (CharField, nullable) - Uses Grade choices
- `electrical_est` (DecimalField, nullable)
- `electrical_grade` (CharField, nullable) - Uses Grade choices
- `landscaping_est` (DecimalField, nullable)
- `landscaping_grade` (CharField, nullable) - Uses Grade choices
- `notes` (TextField, nullable)
- `links` (URLField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)
- `created_by` (FK to User, nullable)
- `updated_by` (FK to User, nullable)

**Unique Together**: `['asset_hub', 'source', 'value_date']`

### ComparableProperty
**Location**: `core/models/model_co_valuations.py`
**Purpose**: Parent model for comparable properties
**Table**: `core_comparable_property`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub, indexed)
- `as_of_date` (DateField, indexed)
- `property_name` (CharField, nullable)
- `street_address` (CharField)
- `city` (CharField)
- `state` (CharField)
- `zip_code` (CharField)
- `distance_from_subject` (IntegerField, nullable)
- `property_type` (CharField, indexed, nullable)
- `property_style` (CharField, nullable)
- `beds` (IntegerField, nullable)
- `baths` (DecimalField, nullable)
- `units` (IntegerField, nullable)
- `gross_square_ft_building` (IntegerField, nullable)
- `livable_square_ft_building` (IntegerField, nullable)
- `year_built` (IntegerField, nullable)
- `total_lot_size` (IntegerField, nullable)
- `market_type` (CharField, nullable)
- `submarket` (CharField, nullable)
- `building_class` (CharField, nullable)
- `notes` (TextField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Relationships**:
- **1:1 with SalesComparable** (via `sales_data`)
- **1:1 with LeaseComparable** (via `lease_data`)
- **1:Many with LeaseComparableUnitMix** (via `lease_unit_mix`)
- **1:Many with LeaseComparableRentRoll** (via `lease_units`)

### SalesComparable
**Location**: `core/models/model_co_valuations.py`
**Purpose**: Sales-specific comparable data
**Table**: `core_sales_comparable`

**Fields**:
- `id` (PK, AutoField)
- `comparable_property` (OneToOneField to ComparableProperty)
- `current_listed_price` (DecimalField, nullable)
- `current_listed_date` (DateField, nullable)
- `last_sales_price` (DecimalField, nullable)
- `last_sales_date` (DateField, nullable)
- `comp_rating` (PositiveSmallIntegerField, nullable) - Choices: 1-5
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### LeaseComparable
**Location**: `core/models/model_co_valuations.py`
**Purpose**: Lease-specific comparable data
**Table**: `core_lease_comparable`

**Fields**:
- `id` (PK, AutoField)
- `comparable_property` (OneToOneField to ComparableProperty)
- `monthly_rent` (DecimalField, nullable)
- `lease_start_date` (DateField, nullable)
- `lease_end_date` (DateField, nullable)
- `lease_term_months` (IntegerField, nullable)
- `lease_type` (CharField, nullable)
- `lease_escalation` (DecimalField, nullable)
- `lease_escalation_frequency` (CharField, nullable)
- `cam_monthly` (DecimalField, nullable)
- `comp_rating` (PositiveSmallIntegerField, nullable) - Choices: 1-5
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### LeaseComparableUnitMix
**Location**: `core/models/model_co_valuations.py`
**Purpose**: Unit mix data for lease comparables
**Table**: `core_lease_comparable_unit_mix`

**Fields**:
- `id` (PK, AutoField)
- `comparable_property` (FK to ComparableProperty, indexed)
- `unit_type` (CharField)
- `unit_count` (IntegerField)
- `unit_avg_sqft` (IntegerField)
- `unit_avg_rent` (DecimalField)
- `price_sqft` (DecimalField, nullable, editable=False)
- `notes` (TextField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### LeaseComparableRentRoll
**Location**: `core/models/model_co_valuations.py`
**Purpose**: Unit-level rent roll for lease comparables
**Table**: `core_lease_comparable_unit`

**Fields**:
- `id` (PK, AutoField)
- `comparable_property` (FK to ComparableProperty, indexed)
- `unit_number` (CharField, nullable)
- `beds` (IntegerField, nullable)
- `baths` (DecimalField, nullable)
- `unit_sqft` (IntegerField, nullable)
- `monthly_rent` (DecimalField, nullable)
- `lease_start_date` (DateField, nullable)
- `lease_end_date` (DateField, nullable)
- `lease_term_months` (IntegerField, nullable)
- `lease_type` (CharField, nullable)
- `lease_escalation` (DecimalField, nullable)
- `lease_escalation_frequency` (CharField, nullable)
- `cam_monthly` (DecimalField, nullable)
- `is_occupied` (BooleanField, default True, indexed)
- `tenant_name` (CharField, nullable)
- `notes` (TextField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

---

## Geographic Reference Models

### StateReference
**Location**: `core/models/model_co_geoAssumptions.py`
**Purpose**: State-specific data and regulations
**Table**: `state_reference`

**Fields**:
- `state_code` (CharField, PK, max 2, indexed)
- `state_name` (CharField)
- `judicialvsnonjudicial` (BooleanField, default False)
- `fc_state_months` (IntegerField)
- `eviction_duration` (IntegerField)
- `rehab_duration` (IntegerField)
- `reo_marketing_duration` (IntegerField)
- `reo_local_market_ext_duration` (IntegerField)
- `dil_duration_avg` (IntegerField)
- `property_tax_rate` (DecimalField)
- `transfer_tax_rate` (DecimalField)
- `insurance_rate_avg` (DecimalField)
- `broker_closing_cost_fees_avg` (DecimalField)
- `other_closing_cost_fees_avg` (DecimalField)
- `fc_legal_fees_avg` (DecimalField)
- `dil_cost_avg` (DecimalField)
- `cfk_cost_avg` (DecimalField)
- `value_adjustment_annual` (DecimalField)
- `utility_electric_avg` (DecimalField, default 0)
- `utility_gas_avg` (DecimalField, default 0)
- `utility_water_avg` (DecimalField, default 0)
- `utility_sewer_avg` (DecimalField, default 0)
- `utility_trash_avg` (DecimalField, default 0)
- `utility_other_avg` (DecimalField, default 0)
- `property_management_avg` (DecimalField, default 0)
- `repairs_maintenance_avg` (DecimalField, default 0)
- `marketing_avg` (DecimalField, default 0)
- `security_cost_avg` (DecimalField, default 0)
- `landscaping_avg` (DecimalField, default 0)
- `pool_maintenance_avg` (DecimalField, default 0)
- `trashout_cost_avg` (DecimalField, default 0)
- `renovation_cost_avg` (DecimalField, default 0)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Relationships**:
- **Many:Many with FirmCRM** (via `crm_firms`)
- **Many:Many with MasterCRM** (via `crm_contacts`)
- **1:Many with CountyReference** (via `counties`)
- **1:Many with MSAReference** (via `msas`)
- **1:Many with FCTimelines** (via `fc_timelines`)

### CountyReference
**Location**: `core/models/model_co_geoAssumptions.py`
**Purpose**: County-level reference data
**Table**: `county_reference`

**Fields**:
- `county_fips` (CharField, PK, max 5, indexed)
- `county_name` (CharField, indexed)
- `state` (FK to StateReference, indexed)
- `population` (IntegerField, nullable)
- `county_seat` (CharField, nullable)

### MSAReference
**Location**: `core/models/model_co_geoAssumptions.py`
**Purpose**: MSA (Metropolitan Statistical Area) reference data
**Table**: `msa_reference`

**Fields**:
- `msa_code` (CharField, PK, max 5, indexed)
- `msa_name` (CharField, indexed)
- `state` (FK to StateReference, indexed, nullable)

**Relationships**:
- **Many:Many with MasterCRM** (via `crm_brokers` through BrokerMSAAssignment)

### HUDZIPCBSACrosswalk
**Location**: `core/models/model_co_geoAssumptions.py`
**Purpose**: HUD ZIP-to-CBSA crosswalk data
**Table**: `hud_zip_cbsa_crosswalk`

**Fields**:
- `id` (PK, AutoField)
- `zip_code` (CharField, max 5, indexed)
- `cbsa_code` (CharField, max 5, indexed, nullable)
- `city` (CharField, nullable)
- `state_code` (CharField, max 2, indexed)
- `res_ratio` (DecimalField, default 0)
- `bus_ratio` (DecimalField, default 0)
- `oth_ratio` (DecimalField, default 0)
- `tot_ratio` (DecimalField, indexed, default 0)
- `imported_at` (DateTimeField)

---

## General Ledger & Financial Models

### GeneralLedgerTag
**Location**: `core/models/model_co_generalLedger.py`
**Purpose**: Tags for GL entries
**Table**: `core_gl_tag`

**Fields**:
- `id` (PK, AutoField)
- `name` (CharField, unique)
- `description` (TextField, nullable)
- `created_at` (DateTimeField)

**Relationships**:
- **Many:Many with GeneralLedgerEntries** (via `entries`)

### GeneralLedgerBucket
**Location**: `core/models/model_co_generalLedger.py`
**Purpose**: High-level GL entry categorization
**Table**: `core_gl_bucket`

**Fields**:
- `id` (PK, AutoField)
- `name` (CharField, unique)
- `code` (CharField, unique, nullable)
- `description` (TextField, nullable)
- `is_active` (BooleanField, default True)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Relationships**:
- **1:Many with GeneralLedgerEntries** (via `entries`)

### GeneralLedgerEntries
**Location**: `core/models/model_co_generalLedger.py`
**Purpose**: General ledger transactions
**Table**: `general_ledger_entries`

**Fields**:
- `id` (PK, AutoField)
- `entry` (CharField, unique, indexed)
- `company_name` (CharField, indexed)
- `asset_link` (FK to AssetIdHub, indexed, nullable)
- `loan_number` (CharField, indexed, nullable)
- `asset_hub` (FK to AssetIdHub, indexed, nullable)
- `borrower_name` (CharField, nullable)
- `bucket` (FK to GeneralLedgerBucket, nullable)
- `document_number` (CharField, indexed, nullable)
- `external_document_number` (CharField, nullable)
- `document_type` (CharField, nullable)
- `loan_type` (CharField, nullable)
- `date_funded` (DateField, nullable)
- `posting_date` (DateField, indexed)
- `entry_date` (DateField, indexed)
- `amount` (DecimalField, nullable)
- `credit_amount` (DecimalField, default 0)
- `debit_amount` (DecimalField, default 0)
- `account_number` (CharField, indexed)
- `account_name` (CharField)
- `description` (TextField, nullable)
- `reason_code` (CharField, nullable)
- `comment` (TextField, nullable)
- `cost_center` (CharField, indexed, nullable)
- `cost_center_name` (CharField, nullable)
- `tag` (CharField, indexed, nullable) - Uses EntryTag choices
- `ai_notes` (TextField, nullable)
- `requires_review` (BooleanField, indexed, default False)
- `review_notes` (TextField, nullable)
- `created_by` (FK to User, nullable)
- `updated_by` (FK to User, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Relationships**:
- **Many:Many with GeneralLedgerTag** (via `tags`)

### ChartOfAccounts
**Location**: `core/models/model_co_generalLedger.py`
**Purpose**: Chart of accounts
**Table**: `chart_of_accounts`

**Fields**:
- `id` (PK, AutoField)
- `account_number` (CharField, unique, indexed)
- `account_name` (CharField)
- `account_type` (CharField)
- `transaction_table_reference` (CharField, nullable)

### LLTransactionSummary
**Location**: `core/models/model_co_realizedTransactions.py`
**Purpose**: Loan-level transaction summary rollup
**Table**: `ll_transaction_summary`

**Fields**:
- `asset_hub` (OneToOneField to AssetIdHub, PK)
- `purchase_price_realized` (DecimalField, nullable)
- `gross_purchase_price_realized` (DecimalField, nullable)
- `acq_due_diligence_realized` (DecimalField, nullable)
- `acq_legal_realized` (DecimalField, nullable)
- `acq_title_realized` (DecimalField, nullable)
- `acq_other_realized` (DecimalField, nullable)
- `income_principal_realized` (DecimalField, nullable)
- `income_interest_realized` (DecimalField, nullable)
- `income_rent_realized` (DecimalField, nullable)
- `income_cam_realized` (DecimalField, nullable)
- `income_mod_down_payment_realized` (DecimalField, nullable)
- `expense_other_realized` (DecimalField, nullable)
- `expense_servicing_realized` (DecimalField, nullable)
- `expense_am_fees_realized` (DecimalField, nullable)
- `expense_property_tax_realized` (DecimalField, nullable)
- `expense_property_insurance_realized` (DecimalField, nullable)
- `legal_foreclosure_realized` (DecimalField, nullable)
- `legal_bankruptcy_realized` (DecimalField, nullable)
- `legal_dil_realized` (DecimalField, nullable)
- `legal_cash_for_keys_realized` (DecimalField, nullable)
- `legal_eviction_realized` (DecimalField, nullable)
- `reo_hoa_realized` (DecimalField, nullable)
- `reo_utilities_realized` (DecimalField, nullable)
- `reo_trashout_realized` (DecimalField, nullable)
- `reo_renovation_realized` (DecimalField, nullable)
- `reo_property_preservation_realized` (DecimalField, nullable)
- `cre_marketing_realized` (DecimalField, nullable)
- `cre_ga_pool_realized` (DecimalField, nullable)
- `cre_maintenance_realized` (DecimalField, nullable)
- `fund_taxes_realized` (DecimalField, nullable)
- `fund_legal_realized` (DecimalField, nullable)
- `fund_consulting_realized` (DecimalField, nullable)
- `fund_audit_realized` (DecimalField, nullable)
- `broker_closing_realized` (DecimalField, nullable)
- `other_closing_realized` (DecimalField, nullable)
- `reo_closing_cost_realized` (DecimalField, nullable)
- `acq_total_realized` (DecimalField, nullable)
- `operating_expenses_total_realized` (DecimalField, nullable)
- `legal_total_realized` (DecimalField, nullable)
- `reo_total_realized` (DecimalField, nullable)
- `cre_total_realized` (DecimalField, nullable)
- `fund_total_realized` (DecimalField, nullable)
- `rehab_trashout_total_realized` (DecimalField, nullable)
- `total_expenses_realized` (DecimalField, nullable)
- `gross_liquidation_proceeds_realized` (DecimalField, nullable)
- `net_liquidation_proceeds_realized` (DecimalField, nullable)
- `realized_gross_cost` (DecimalField, nullable)
- `last_updated` (DateTimeField, auto_now)
- `created_at` (DateTimeField)

### LLCashFlowSeries
**Location**: `core/models/model_co_realizedTransactions.py`
**Purpose**: Period-by-period cash flow breakdown
**Table**: `ll_cash_flow_series`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (FK to AssetIdHub, indexed)
- `period_date` (DateField, indexed)
- `period_number` (IntegerField, indexed)
- `purchase_price` (DecimalField, default 0)
- `acq_due_diligence_expenses` (DecimalField, default 0)
- `acq_legal_expenses` (DecimalField, default 0)
- `acq_title_expenses` (DecimalField, default 0)
- `acq_other_expenses` (DecimalField, default 0)
- `income_principal` (DecimalField, default 0)
- `income_interest` (DecimalField, default 0)
- `income_rent` (DecimalField, default 0)
- `income_cam` (DecimalField, default 0)
- `income_mod_down_payment` (DecimalField, default 0)
- `servicing_expenses` (DecimalField, default 0)
- `am_fees_expenses` (DecimalField, default 0)
- `property_tax_expenses` (DecimalField, default 0)
- `property_insurance_expenses` (DecimalField, default 0)
- `legal_foreclosure_expenses` (DecimalField, default 0)
- `legal_bankruptcy_expenses` (DecimalField, default 0)
- `legal_dil_expenses` (DecimalField, default 0)
- `legal_cash_for_keys_expenses` (DecimalField, default 0)
- `legal_eviction_expenses` (DecimalField, default 0)
- `reo_hoa_expenses` (DecimalField, default 0)
- `reo_utilities_expenses` (DecimalField, default 0)
- `reo_trashout_expenses` (DecimalField, default 0)
- `reo_renovation_expenses` (DecimalField, default 0)
- `reo_property_preservation_expenses` (DecimalField, default 0)
- `cre_marketing_expenses` (DecimalField, default 0)
- `cre_ga_pool_expenses` (DecimalField, default 0)
- `cre_maintenance_expenses` (DecimalField, default 0)
- `fund_taxes_expenses` (DecimalField, default 0)
- `fund_legal_expenses` (DecimalField, default 0)
- `fund_consulting_expenses` (DecimalField, default 0)
- `fund_audit_expenses` (DecimalField, default 0)
- `proceeds` (DecimalField, default 0)
- `broker_closing_expenses` (DecimalField, default 0)
- `other_closing_expenses` (DecimalField, default 0)
- `net_liquidation_proceeds` (DecimalField, default 0)
- `total_income` (DecimalField, default 0)
- `total_expenses` (DecimalField, default 0)
- `net_cash_flow` (DecimalField, default 0)

**Unique Together**: `['asset_hub', 'period_date']`

### LlDataEnrichment
**Location**: `core/models/model_co_enrichment.py`
**Purpose**: Supplemental/derived analysis for assets
**Table**: `acq_ll_data_enrichment`

**Fields**:
- `id` (PK, AutoField)
- `asset_hub` (OneToOneField to AssetIdHub, indexed, nullable)
- `geocode_lat` (DecimalField, nullable)
- `geocode_lng` (DecimalField, nullable)
- `geocode_used_address` (CharField, nullable)
- `geocode_full_address` (CharField, nullable)
- `geocode_display_address` (CharField, nullable)
- `geocoded_at` (DateTimeField, nullable)
- `geocode_county` (CharField, nullable)
- `geocode_msa` (CharField, nullable)
- `geocode_msa_code` (CharField, nullable)
- `geocode_state_fips` (CharField, nullable)
- `geocode_county_fips` (CharField, nullable)
- `geocode_tract_code` (CharField, nullable)
- `geocode_full_fips` (CharField, nullable)
- `geocode_msa_type` (CharField, nullable)
- `geocode_csa_name` (CharField, nullable)
- `geocode_csa_code` (CharField, nullable)
- `geocode_county_name` (CharField, nullable)
- `geocode_block_code` (CharField, nullable)
- `geocode_block_group` (CharField, nullable)
- `geocode_place_name` (CharField, nullable)
- `geocode_place_fips` (CharField, nullable)
- `geocode_metdiv_name` (CharField, nullable)
- `geocode_metdiv_code` (CharField, nullable)
- `geocode_county_subdivision_name` (CharField, nullable)
- `geocode_county_subdivision_fips` (CharField, nullable)
- `geocode_county_subdivision_class_code` (CharField, nullable)
- `geocode_county_subdivision_class_desc` (CharField, nullable)
- `geocode_census_year` (CharField, nullable)
- `geocode_census_source` (CharField, nullable)
- `geocode_school_district` (CharField, nullable)
- `geocode_school_district_lea_code` (CharField, nullable)
- `geocode_school_district_grade_low` (CharField, nullable)
- `geocode_school_district_grade_high` (CharField, nullable)
- `geocode_school_district_type` (CharField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### AuditLog
**Location**: `am_module/models/model_am_amData.py`
**Purpose**: Generic audit log for tracking changes
**Table**: `am_auditlog`

**Fields**:
- `id` (PK, AutoField)
- `content_type` (FK to ContentType)
- `object_id` (PositiveIntegerField)
- `asset_hub` (FK to AssetIdHub, indexed, nullable)
- `field_name` (CharField, indexed)
- `old_value` (TextField, nullable)
- `new_value` (TextField, nullable)
- `changed_at` (DateTimeField, indexed)
- `changed_by` (FK to User, indexed, nullable)

---

## ETL & Import Models

**Note**: ETL models exist in `etl/models/` but were not fully read in this scan. Based on the glob results, these include:
- `model_etl_valueImports.py`
- `model_etl_statebridge_raw.py`
- `model_etl_document_extraction.py`

---

## Model Relationship Summary

### Hub-Centric Architecture
**AssetIdHub** is the central hub that connects all asset-related data:

1. **Acquisition Data** (1:1):
   - SellerRawData
   - AssetDetails
   - LlDataEnrichment

2. **Financial Data** (1:1 or 1:Many):
   - LLTransactionSummary (1:1)
   - LLCashFlowSeries (1:Many)
   - GeneralLedgerEntries (1:Many)
   - LoanLevelAssumption (1:Many)

3. **Valuation Data** (1:Many):
   - Valuation
   - ComparableProperty

4. **Asset Management Outcomes** (1:1 each):
   - REOData
   - FCSale
   - DIL
   - ShortSale
   - Modification
   - NoteSale

5. **Asset Management Tasks** (1:Many each):
   - REOtask
   - FCTask
   - DILTask
   - ShortSaleTask
   - ModificationTask
   - NoteSaleTask

6. **Supporting Data** (1:Many):
   - AMMetrics
   - AMNote
   - AssetCRMContact
   - REOScope
   - Offers

### Trade Hierarchy
```
Seller (1:Many) → Trade (1:Many) → SellerRawData (1:1) → AssetIdHub
                                  ↓
                          TradeLevelAssumption
```

### Fund Structure
```
Entity (1:Many) → FundLegalEntity (1:Many) → AssetDetails
       ↓
FundMembership (Many:Many with Entity)
       ↓
EntityMembership (self-referential)
```

### Capital Structure
```
CoInvestor (1:Many) → InvestorContribution
                   → InvestorDistribution
```

### CRM Structure
```
FirmCRM (1:Many) → MasterCRM (Many:Many) → AssetCRMContact → AssetIdHub
                           ↓
                   BrokerMSAAssignment → MSAReference
```

### Geographic Hierarchy
```
StateReference (1:Many) → CountyReference
                       → MSAReference
                       → FCTimelines → FCStatus
```

---

## Key Foreign Key Relationships for Factory Boy

### Critical Dependencies (Must Create First):
1. **StateReference** - No dependencies
2. **MSAReference** - Depends on StateReference
3. **CountyReference** - Depends on StateReference
4. **FirmCRM** - Depends on StateReference (M2M)
5. **MasterCRM** - Depends on FirmCRM, StateReference, MSAReference
6. **Seller** - No dependencies
7. **Trade** - Depends on Seller
8. **Entity** - No dependencies
9. **FundLegalEntity** - Depends on Entity
10. **AssetIdHub** - No dependencies (central hub)

### Secondary Dependencies (Create After Hub):
11. **SellerRawData** - Depends on AssetIdHub, Seller, Trade
12. **AssetDetails** - Depends on AssetIdHub, FundLegalEntity, Trade
13. **Servicer** - No dependencies
14. **TradeLevelAssumption** - Depends on Trade, Servicer
15. **LoanLevelAssumption** - Depends on AssetIdHub

### Tertiary Dependencies (Create After Core Data):
16. **Valuation** - Depends on AssetIdHub, MasterCRM
17. **ComparableProperty** - Depends on AssetIdHub
18. **REOData** - Depends on AssetIdHub
19. **FCSale** - Depends on AssetIdHub
20. **DIL** - Depends on AssetIdHub
21. **ShortSale** - Depends on AssetIdHub
22. **Modification** - Depends on AssetIdHub
23. **NoteSale** - Depends on AssetIdHub, MasterCRM

### Final Dependencies (Create Last):
24. **REOtask** - Depends on AssetIdHub, REOData
25. **FCTask** - Depends on AssetIdHub, FCSale
26. **DILTask** - Depends on AssetIdHub, DIL
27. **ShortSaleTask** - Depends on AssetIdHub, ShortSale
28. **ModificationTask** - Depends on AssetIdHub, Modification
29. **NoteSaleTask** - Depends on AssetIdHub, NoteSale
30. **GeneralLedgerEntries** - Depends on AssetIdHub, GeneralLedgerBucket
31. **LLTransactionSummary** - Depends on AssetIdHub
32. **LLCashFlowSeries** - Depends on AssetIdHub

---

## Next Steps for Test Data Creation

### Phase 1: Setup Factory Boy & Faker
1. Install dependencies: `pip install factory-boy faker`
2. Create `factories/` directory structure
3. Set up base factory configuration

### Phase 2: Create Reference Data Factories
1. Geographic references (State, County, MSA)
2. Lookup tables and assumptions
3. CRM and contact data
4. Servicer data

### Phase 3: Create Core Entity Factories
1. Seller and Trade factories
2. Entity and Fund structure factories
3. AssetIdHub factory (central hub)

### Phase 4: Create Asset Data Factories
1. SellerRawData factory
2. AssetDetails factory
3. Valuation factories
4. Comparable property factories

### Phase 5: Create Outcome & Task Factories
1. REO, FC, DIL, ShortSale, Modification, NoteSale factories
2. Associated task factories for each outcome
3. Supporting data (Offers, REOScope, etc.)

### Phase 6: Create Financial Data Factories
1. GeneralLedgerEntries factory
2. LLTransactionSummary factory
3. LLCashFlowSeries factory

### Phase 7: Management Command
1. Create management command to clear all data
2. Create management command to generate interconnected test data
3. Add parameters for data volume and complexity

---

**End of Document**
