"""
ETL Package for Seller Data Import

WHAT: Modular ETL system for importing seller loan tape data
WHY: Separates concerns - Outlook scanning, seller rules, AI mapping, file processing, data import
HOW: Each module handles one specific aspect of the ETL pipeline

Modules:
- outlook_scanner: Email scanning and attachment downloading
- seller_rules: Seller identification and password extraction
- ai_mapper: AI-powered column mapping
- file_processor: Excel/CSV reading and decryption
- data_importer: Database import and seller/trade management
"""

from .outlook_scanner import OutlookScanner
from .seller_rules import SellerIdentifier, SELLER_RULES
from .ai_mapper import AIColumnMapper
from .file_processor import FileProcessor
from .data_importer import DataImporter

__all__ = [
    'OutlookScanner',
    'SellerIdentifier',
    'SELLER_RULES',
    'AIColumnMapper',
    'FileProcessor',
    'DataImporter',
]
