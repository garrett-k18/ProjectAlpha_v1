"""
Seller Rules and Identification Module

WHAT: Defines seller-specific rules for email processing and password extraction
WHY: Each seller has unique email formats, password patterns, and requirements
HOW: Maintains SELLER_RULES dict and provides SellerIdentifier class for matching

USAGE:
    identifier = SellerIdentifier()
    seller_rules = identifier.identify(email_data)
    if seller_rules:
        password = seller_rules.extract_password(email_data)
"""

import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# SELLER-SPECIFIC CONFIGURATION
# ============================================================================
# WHAT: Define how to handle emails and passwords from different sellers
# WHY: Each seller has unique email formats, password patterns, and folder locations
# HOW: Add entries to SELLER_RULES dict for each seller you receive data from

SELLER_RULES = {
    'SitusAMC': {
        'email_domain': 'situsamc.com',  # Match emails from @situsamc.com
        'subject_contains': 'SitusAMC',  # Additional subject filter
        'outlook_folder': 'Data Tape Import',  # Outlook folder name (root level)
        'has_password': True,
        'password_pattern': r'SA\d{5}\$',  # Pattern: SA##### followed by $ (entire password on own line)
        'password_source': 'body',  # Extract from 'subject' or 'body'
        'attachment_filter': 'Data Tape',  # Only process attachments with this in filename
    },

    # Add more sellers here as needed:
    # 'SellerName': {
    #     'email_domain': 'example.com',
    #     'subject_contains': 'Loan Tape',
    #     'outlook_folder': 'Data Tape Import',
    #     'has_password': False,
    #     'attachment_filter': None,  # Process all Excel attachments
    # },
}

# DEFAULT SETTINGS for emails that don't match any seller rule
DEFAULT_OUTLOOK_FOLDER = 'Inbox'  # Default folder if no seller match


class SellerRule:
    """
    WHAT: Represents a matched seller with their specific rules
    WHY: Encapsulates seller-specific logic for password extraction and validation
    HOW: Created by SellerIdentifier when a seller is matched
    """

    def __init__(self, name: str, rules: Dict[str, Any]):
        self.name = name
        self.rules = rules
        self.email_domain = rules.get('email_domain')
        self.subject_contains = rules.get('subject_contains')
        self.outlook_folder = rules.get('outlook_folder', DEFAULT_OUTLOOK_FOLDER)
        self.has_password = rules.get('has_password', False)
        self.password_pattern = rules.get('password_pattern')
        self.password_source = rules.get('password_source', 'body')
        self.attachment_filter = rules.get('attachment_filter')

    def extract_password(self, email: Dict[str, Any]) -> Optional[str]:
        """
        WHAT: Extract password from email based on seller-specific rules
        WHY: Each seller has different password formats and locations
        HOW: Use password_pattern and password_source to find password in email

        Args:
            email: Email data from Microsoft Graph API

        Returns:
            Extracted password string or None
        """
        if not self.has_password or not self.password_pattern:
            return None

        # Determine where to look for password
        if self.password_source == 'subject':
            search_text = email.get('subject', '')
        elif self.password_source == 'body':
            search_text = email.get('body', {}).get('content', '')
        else:
            search_text = email.get('body', {}).get('content', '')

        # Extract password using regex pattern
        match = re.search(self.password_pattern, search_text, re.IGNORECASE)
        if match:
            password = match.group(0)
            logger.info(f'Found password using {self.name} rule: {password}')
            return password

        logger.warning(f'Password pattern not found in {self.password_source} for {self.name}')
        return None

    def matches_attachment(self, filename: str) -> bool:
        """
        WHAT: Check if attachment filename matches seller's filter
        WHY: Some sellers send multiple attachments, only some are data files
        HOW: Check if attachment_filter substring is in filename

        Args:
            filename: Attachment filename

        Returns:
            True if attachment should be processed, False otherwise
        """
        if not self.attachment_filter:
            return True  # No filter = process all

        return self.attachment_filter in filename

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict format (for backward compatibility)"""
        return {'name': self.name, **self.rules}


class SellerIdentifier:
    """
    WHAT: Identifies which seller an email is from
    WHY: Different sellers need different processing rules
    HOW: Matches email metadata against SELLER_RULES
    """

    @staticmethod
    def identify(email: Dict[str, Any]) -> Optional[SellerRule]:
        """
        WHAT: Identify which seller this email is from and return their rules
        WHY: Different sellers have different password patterns and requirements
        HOW: Check sender email domain and subject against SELLER_RULES

        Args:
            email: Email data from Microsoft Graph API with 'from' and 'subject' fields

        Returns:
            SellerRule instance if matched, None otherwise
        """
        sender_email = email.get('from', {}).get('emailAddress', {}).get('address', '').lower()
        subject = email.get('subject', '').lower()

        for seller_name, rules in SELLER_RULES.items():
            # Check if sender domain matches
            if 'email_domain' in rules and rules['email_domain'].lower() in sender_email:
                # Additional subject check if specified
                if 'subject_contains' in rules:
                    if rules['subject_contains'].lower() in subject:
                        logger.info(f'Identified seller: {seller_name}')
                        return SellerRule(seller_name, rules)
                else:
                    logger.info(f'Identified seller: {seller_name}')
                    return SellerRule(seller_name, rules)

        logger.debug('No seller matched for this email')
        return None

    @staticmethod
    def identify_with_ai_fallback(email: Dict[str, Any], ai_extracted_name: Optional[str] = None) -> Optional[SellerRule]:
        """
        WHAT: Enhanced seller identification with AI fallback support
        WHY: Combines rule-based matching with AI-extracted seller names for better coverage
        HOW: First try rule-based matching, then check if AI-extracted name matches any rules

        Args:
            email: Email data from Microsoft Graph API
            ai_extracted_name: Seller name extracted by AI (optional)

        Returns:
            SellerRule instance if matched, None otherwise
        """
        # First, try standard rule-based identification
        seller_rule = SellerIdentifier.identify(email)
        if seller_rule:
            return seller_rule

        # If no rule match and AI provided a seller name, check if it matches any configured sellers
        if ai_extracted_name:
            ai_name_lower = ai_extracted_name.lower().strip()
            
            # Check if AI-extracted name matches any seller rule names (case-insensitive)
            for seller_name, rules in SELLER_RULES.items():
                if seller_name.lower() == ai_name_lower:
                    logger.info(f'AI-extracted seller name "{ai_extracted_name}" matches configured seller: {seller_name}')
                    return SellerRule(seller_name, rules)
                
                # Also check if AI name is contained in rule name or vice versa
                if (ai_name_lower in seller_name.lower() or 
                    seller_name.lower() in ai_name_lower) and len(ai_name_lower) > 3:
                    logger.info(f'AI-extracted seller name "{ai_extracted_name}" partially matches configured seller: {seller_name}')
                    return SellerRule(seller_name, rules)

        logger.debug('No seller matched via rules or AI fallback')
        return None

    @staticmethod
    def get_seller_by_name(seller_name: str) -> Optional[SellerRule]:
        """
        WHAT: Get seller rules by name
        WHY: Useful for testing or manual rule application
        HOW: Direct lookup in SELLER_RULES dict

        Args:
            seller_name: Name of seller (key in SELLER_RULES)

        Returns:
            SellerRule instance if found, None otherwise
        """
        if seller_name in SELLER_RULES:
            return SellerRule(seller_name, SELLER_RULES[seller_name])
        return None

    @staticmethod
    def list_sellers() -> list[str]:
        """
        WHAT: Get list of all configured seller names
        WHY: Useful for debugging and documentation
        HOW: Returns keys from SELLER_RULES dict

        Returns:
            List of seller names
        """
        return list(SELLER_RULES.keys())
