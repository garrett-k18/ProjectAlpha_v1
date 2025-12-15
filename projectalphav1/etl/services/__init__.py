"""Service layer for ETL workflows."""

from etl.services.services_sellerTapeImport.serv_etl_outlook import OutlookScanner
from etl.services.services_sellerTapeImport.serv_etl_seller_rules import SellerIdentifier, SELLER_RULES, SellerRule
from etl.services.services_sellerTapeImport.serv_etl_ai_mapper import AIColumnMapper, validate_choice_value
from etl.services.services_sellerTapeImport.serv_etl_ai_seller_matcher import AISellerMatcher
from etl.services.services_sellerTapeImport.serv_etl_file_processor import FileProcessor
from etl.services.services_sellerTapeImport.serv_etl_data_importer import DataImporter

# Claude client (legacy - deprecated)
from etl.services.services_valuationExtract.serv_etl_claude_client import (
    build_valuation_claude_client,
    build_valuation_claude_vision_client,
)

# Gemini client (new - recommended)
from etl.services.services_valuationExtract.serv_etl_gemini_client import (
    build_valuation_gemini_vision_client,
)

# Optimized extraction (fastest)
from etl.services.services_valuationExtract.serv_etl_gemini_optimized import (
    OptimizedGeminiExtractor,
    quick_extract,
    smart_extract,
)

# Multi-pass extraction (bypasses 120-second server timeout)
from etl.services.services_valuationExtract.serv_etl_gemini_multipass import (
    MultiPassGeminiExtractor,
    multipass_extract,
)

# Vision extractor service (supports both Claude and Gemini)
from etl.services.services_valuationExtract.serv_etl_valuation_vision_extractor import (
    GeminiVisionExtractionService,
    ClaudeVisionExtractionService,  # Alias for backward compatibility
    DocumentExtractionResult,
    FieldExtractionRecord,
)

from etl.services.services_valuationExtract.serv_etl_valuationPipeline import ValuationExtractionPipeline

__all__ = [
    'OutlookScanner',
    'SellerIdentifier',
    'SELLER_RULES',
    'SellerRule',
    'AIColumnMapper',
    'validate_choice_value',
    'AISellerMatcher',
    'FileProcessor',
    'DataImporter',
    # Claude (deprecated)
    'build_valuation_claude_client',
    'build_valuation_claude_vision_client',
    'ClaudeVisionExtractionService',
    # Gemini (recommended)
    'build_valuation_gemini_vision_client',
    'GeminiVisionExtractionService',
    # Optimized (fastest)
    'OptimizedGeminiExtractor',
    'quick_extract',
    'smart_extract',
    # Multi-pass (bypasses 120s timeout)
    'MultiPassGeminiExtractor',
    'multipass_extract',
    # Common
    'DocumentExtractionResult',
    'FieldExtractionRecord',
    'ValuationExtractionPipeline',
]
