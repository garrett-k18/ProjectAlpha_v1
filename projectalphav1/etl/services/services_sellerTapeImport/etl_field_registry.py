"""
ETL Import Field Registry
 
WHAT: Central registry of importable field names and their target models
WHY: Replace legacy SellerRawData field introspection with explicit mappings
HOW: Map legacy field names to AcqAsset/AcqLoan/AcqProperty/FC/Valuation targets
 
Docs reviewed:
- Django model meta API: https://docs.djangoproject.com/en/5.2/ref/models/meta/
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

from acq_module.models.model_acq_seller import (
    AcqAsset,
    AcqLoan,
    AcqProperty,
    AcqForeclosureTimeline,
    AcqBankruptcy,
    AcqModification,
)
from core.models.model_co_valuations import Valuation


@dataclass(frozen=True)
class ImportFieldSpec:
    """
    WHAT: Metadata describing a single importable field
    WHY: Shared structure for AI mapping, manual mapping, and import validation
    HOW: Stores field name, model target, and descriptive metadata
    """
    # WHAT: External field name used by mapping/UI
    # WHY: Keep legacy column names stable for users
    # HOW: String key used in mapping payloads
    name: str
    # WHAT: Target model group for persistence
    # WHY: Route values to the correct model
    # HOW: One of: asset, loan, property, foreclosure, valuation, special
    target_group: str
    # WHAT: Target model field name (or special handler token)
    # WHY: Connect mapping to concrete storage field
    # HOW: Django model field name or special handler name
    target_field: str
    # WHAT: Human-readable description for AI mapping
    # WHY: Provide semantic context to mapping logic and UI
    # HOW: Derived from model help_text or handcrafted
    description: str
    # WHAT: Field type string
    # WHY: UI and conversion logic need type hints
    # HOW: Django internal type or fallback string
    field_type: str


# ---------------------------------------------------------------------------
# Target model lookups
# ---------------------------------------------------------------------------
_MODEL_LOOKUP: Dict[str, Tuple[object, str]] = {
    # WHAT: Map group name to model class
    # WHY: Allow meta introspection for types/help_text
    # HOW: Tuple of (model_class, label)
    "asset": (AcqAsset, "AcqAsset"),
    "loan": (AcqLoan, "AcqLoan"),
    "property": (AcqProperty, "AcqProperty"),
    "foreclosure": (AcqForeclosureTimeline, "AcqForeclosureTimeline"),
    "valuation": (Valuation, "Valuation"),
    "bankruptcy": (AcqBankruptcy, "AcqBankruptcy"),
    "modification": (AcqModification, "AcqModification"),
}


# ---------------------------------------------------------------------------
# Canonical field mappings (legacy field name -> target model field)
# ---------------------------------------------------------------------------
_FIELD_SPECS: Dict[str, Tuple[str, str, Optional[str]]] = {
    # ===== Asset-level =====
    "asset_class": ("asset", "asset_class", "Primary asset class"),
    "asset_status": ("asset", "asset_status", "Legacy asset status (NPL/REO/PERF/RPL)"),
    "acq_status": ("asset", "acq_status", "Acquisition keep/drop status"),
    "real_estate_subclass_type": ("asset", "real_estate_subclass_type", "Real estate subclass"),
    "multifamily_subclass_type": ("asset", "multifamily_subclass_type", "Multifamily subclass"),
    "commercial_subclass_type": ("asset", "commercial_subclass_type", "Commercial subclass"),
    "note_subclass_type": ("asset", "note_subclass_type", "Note subclass (NPL/PERF/RPL)"),

    # ===== Loan identifiers =====
    "sellertape_id": ("loan", "sellertape_id", "Seller-provided primary identifier"),
    "sellertape_altid": ("loan", "sellertape_altid", "Seller-provided alternate identifier"),

    # ===== Loan financials =====
    "current_balance": ("loan", "current_balance", "Unpaid principal balance"),
    "total_debt": ("loan", "total_debt", "Total debt (UPB + fees/advances)"),
    "interest_rate": ("loan", "interest_rate", "Current interest rate"),
    "default_rate": ("loan", "default_rate", "Default interest rate"),
    "next_due_date": ("loan", "next_due_date", "Next due date"),
    "last_paid_date": ("loan", "last_paid_date", "Last paid date"),
    "first_pay_date": ("loan", "first_pay_date", "First pay date"),
    "origination_date": ("loan", "origination_date", "Origination date"),
    "original_balance": ("loan", "original_balance", "Original balance"),
    "original_term": ("loan", "original_term", "Original term (months)"),
    "original_rate": ("loan", "original_rate", "Original rate"),
    "original_maturity_date": ("loan", "original_maturity_date", "Original maturity date"),
    "current_maturity_date": ("loan", "current_maturity_date", "Current maturity date"),
    "current_term": ("loan", "current_term", "Current term (months)"),
    "months_delinquent": ("loan", "months_dlq", "Months delinquent"),

    # ===== Origination valuation (loan-level + valuation sync) =====
    "origination_value": ("loan", "origination_value", "Origination as-is value"),
    "origination_arv": ("loan", "origination_arv", "Origination ARV value"),
    "origination_value_date": ("loan", "origination_value_date", "Origination value date"),

    # ===== Loan product/borrower =====
    "product_type": ("loan", "product_type", "Loan product type"),
    "borrower1_last": ("loan", "borrower1_last", "Borrower 1 last name"),
    "borrower1_first": ("loan", "borrower1_first", "Borrower 1 first name"),
    "borrower2_last": ("loan", "borrower2_last", "Borrower 2 last name"),
    "borrower2_first": ("loan", "borrower2_first", "Borrower 2 first name"),

    # ===== Property address =====
    "street_address": ("property", "street_address", "Street address"),
    "city": ("property", "city", "City"),
    "state": ("property", "state", "State"),
    "zip": ("property", "zip", "Postal code"),

    # ===== Property characteristics =====
    "occupancy": ("property", "occupancy", "Occupancy status"),
    "year_built": ("property", "year_built", "Year built"),
    "sqft": ("property", "sq_ft", "Square footage"),
    "beds": ("property", "beds", "Bedrooms"),
    "bedrooms": ("property", "beds", "Bedrooms"),
    "baths": ("property", "baths", "Bathrooms"),
    "bathrooms": ("property", "baths", "Bathrooms"),
    "lot_size": ("property", "lot_size", "Lot size"),

    # ===== Foreclosure timeline =====
    "fc_flag": ("foreclosure", "fc_flag", "Foreclosure flag"),
    "fc_first_legal_date": ("foreclosure", "fc_first_legal_date", "FC first legal date"),
    "fc_referred_date": ("foreclosure", "fc_referred_date", "FC referred date"),
    "fc_judgement_date": ("foreclosure", "fc_judgement_date", "FC judgement date"),
    "fc_scheduled_sale_date": ("foreclosure", "fc_scheduled_sale_date", "FC scheduled sale date"),
    "fc_sale_date": ("foreclosure", "fc_sale_date", "FC sale date"),
    "fc_starting": ("foreclosure", "fc_starting", "FC starting amount"),

    # ===== Bankruptcy =====
    "bk_flag": ("bankruptcy", "bk_flag", "Bankruptcy flag"),
    "bk_chapter": ("bankruptcy", "bk_chapter", "Bankruptcy chapter"),

    # ===== Modification =====
    "mod_flag": ("modification", "mod_flag", "Modification flag"),
    "mod_date": ("modification", "mod_date", "Modification date"),
    "mod_maturity_date": ("modification", "mod_maturity_date", "Modification maturity date"),
    "mod_term": ("modification", "mod_term", "Modification term"),
    "mod_rate": ("modification", "mod_rate", "Modification rate"),
    "mod_initial_balance": ("modification", "mod_initial_balance", "Modification initial balance"),

    # ===== Seller valuation fields =====
    "seller_asis_value": ("valuation", "asis_value", "Seller-provided as-is value"),
    "seller_arv_value": ("valuation", "arv_value", "Seller-provided ARV value"),
    "seller_value_date": ("valuation", "value_date", "Seller valuation date"),
    "additional_asis_value": ("valuation", "asis_value", "Additional seller as-is value"),
    "additional_arv_value": ("valuation", "arv_value", "Additional seller ARV value"),
    "additional_value_date": ("valuation", "value_date", "Additional seller valuation date"),

    # ===== Special handlers =====
    "property_type": ("special", "property_type", "Legacy property type; maps to subclass"),
}


def get_import_field_specs() -> Dict[str, ImportFieldSpec]:
    """
    WHAT: Build ImportFieldSpec objects for all supported field names
    WHY: Provide consistent metadata for AI mapping and UI target lists
    HOW: Resolve Django field types/help_text when possible
    """
    specs: Dict[str, ImportFieldSpec] = {}

    for field_name, (group, target_field, override_desc) in _FIELD_SPECS.items():
        # WHAT: Default metadata
        # WHY: Provide safe fallbacks for special fields
        # HOW: Use string fallbacks when no Django field exists
        field_type = "CharField"
        description = override_desc or field_name

        # WHAT: Try to resolve from model meta
        # WHY: Preserve real field types and help_text when available
        # HOW: Use Django _meta.get_field for concrete model fields
        if group in _MODEL_LOOKUP and group != "special":
            model_cls = _MODEL_LOOKUP[group][0]
            try:
                model_field = model_cls._meta.get_field(target_field)
                field_type = model_field.get_internal_type()
                description = override_desc or getattr(model_field, "help_text", "") or f"{field_name} ({field_type})"
            except Exception:
                # WHAT: Fallback to safe defaults if field not found
                # WHY: Prevent registry failure when field names evolve
                # HOW: Keep description/type defaults
                pass

        specs[field_name] = ImportFieldSpec(
            name=field_name,
            target_group=group,
            target_field=target_field,
            description=description,
            field_type=field_type,
        )

    return specs


def get_import_field_definitions() -> Dict[str, Dict[str, str]]:
    """
    WHAT: Return AI-friendly field definitions for mapping prompts
    WHY: Provide consistent descriptions for Claude mapping
    HOW: Convert ImportFieldSpec objects to simple dicts
    """
    specs = get_import_field_specs()
    return {
        name: {"type": spec.field_type, "description": spec.description}
        for name, spec in specs.items()
    }


def get_import_field_targets() -> Dict[str, Tuple[str, str]]:
    """
    WHAT: Return target group/field mapping for import routing
    WHY: Split flat record data into model-specific dicts
    HOW: Build dict of {field_name: (group, target_field)}
    """
    specs = get_import_field_specs()
    return {name: (spec.target_group, spec.target_field) for name, spec in specs.items()}
