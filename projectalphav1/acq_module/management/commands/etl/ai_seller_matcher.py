"""
AI Seller Name Extraction and Matching Module

WHAT: Intelligently extracts seller names from emails and matches to existing Seller records
WHY: Automates seller identification during email processing to reduce manual data entry
HOW: Uses Claude AI for name extraction + fuzzy matching for existing seller lookup

USAGE:
    matcher = AISellerMatcher()
    seller = matcher.match_or_create_seller(email_data, file_path)
    # Returns existing Seller or creates new one
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from difflib import SequenceMatcher
from pathlib import Path

import anthropic
from django.db import transaction

from acq_module.models.seller import Seller, Trade

logger = logging.getLogger(__name__)


class AISellerMatcher:
    """
    WHAT: AI-powered seller name extraction and matching system
    WHY: Automates seller identification from email content and file names
    HOW: Uses Claude AI for extraction + fuzzy matching for existing seller lookup
    """

    def __init__(self, stdout=None, similarity_threshold: float = 0.7):
        """
        Initialize AI seller matcher

        Args:
            stdout: Django stdout for progress messages (optional)
            similarity_threshold: Minimum similarity score for fuzzy matching (0.0-1.0)
        """
        self.stdout = stdout
        self.similarity_threshold = similarity_threshold
        self._seller_cache = {}  # Cache existing sellers for performance

    def match_or_create_seller(
        self,
        email_data: Optional[Dict[str, Any]] = None,
        file_path: Optional[Path] = None,
        seller_name_hint: Optional[str] = None
    ) -> Seller:
        """
        WHAT: Main entry point - extract seller name and match/create Seller record
        WHY: Single method to handle all seller identification logic
        HOW: Extract name from multiple sources, match existing, or create new

        Args:
            email_data: Email metadata from Outlook scanner (optional)
            file_path: Path to data file (optional)
            seller_name_hint: Manual seller name override (optional)

        Returns:
            Seller instance (existing or newly created)
        """
        # Step 1: Extract seller name from available sources
        extracted_name = self._extract_seller_name(email_data, file_path, seller_name_hint)
        
        if not extracted_name:
            # Fallback: create generic seller name
            extracted_name = self._generate_fallback_name(email_data, file_path)

        if self.stdout:
            self.stdout.write(f'   [AI-SELLER] Extracted seller name: "{extracted_name}"\n')

        # Step 2: Try to match existing seller
        existing_seller = self._find_matching_seller(extracted_name)
        
        if existing_seller:
            if self.stdout:
                self.stdout.write(f'   [AI-SELLER] Matched existing seller: "{existing_seller.name}" (ID: {existing_seller.id})\n')
            return existing_seller

        # Step 3: Create new seller if no match found
        new_seller = self._create_new_seller(extracted_name, email_data)
        
        if self.stdout:
            self.stdout.write(f'   [AI-SELLER] Created new seller: "{new_seller.name}" (ID: {new_seller.id})\n')
        
        return new_seller

    def _extract_seller_name(
        self,
        email_data: Optional[Dict[str, Any]],
        file_path: Optional[Path],
        seller_name_hint: Optional[str]
    ) -> Optional[str]:
        """
        WHAT: Extract seller name from multiple sources using AI and heuristics
        WHY: Seller names can appear in email subjects, bodies, filenames, or sender info
        HOW: Try AI extraction first, then fallback to heuristic methods

        Args:
            email_data: Email metadata
            file_path: File path
            seller_name_hint: Manual override

        Returns:
            Extracted seller name or None
        """
        # Priority 1: Manual hint (highest priority)
        if seller_name_hint and seller_name_hint.strip():
            return self._clean_seller_name(seller_name_hint.strip())

        # Priority 2: AI extraction from email content
        if email_data:
            ai_extracted = self._ai_extract_seller_name(email_data)
            if ai_extracted:
                return ai_extracted

        # Priority 3: Heuristic extraction from filename
        if file_path:
            filename_extracted = self._extract_from_filename(file_path)
            if filename_extracted:
                return filename_extracted

        # Priority 4: Extract from email sender domain
        if email_data:
            domain_extracted = self._extract_from_sender_domain(email_data)
            if domain_extracted:
                return domain_extracted

        return None

    def _ai_extract_seller_name(self, email_data: Dict[str, Any]) -> Optional[str]:
        """
        WHAT: Use Claude AI to intelligently extract seller name from email content
        WHY: AI can understand context and identify seller names in natural language
        HOW: Send email subject/body to Claude with specific instructions

        Args:
            email_data: Email metadata with subject and body

        Returns:
            Extracted seller name or None
        """
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            if self.stdout:
                self.stdout.write('   [AI-SELLER] ANTHROPIC_API_KEY not found, skipping AI extraction\n')
            return None

        try:
            # Prepare email content for AI analysis
            subject = email_data.get('subject', '')
            body_content = email_data.get('body', {}).get('content', '')
            sender_email = email_data.get('from', {}).get('emailAddress', {}).get('address', '')
            sender_name = email_data.get('from', {}).get('emailAddress', {}).get('name', '')

            # Create AI prompt for seller name extraction
            prompt = f"""You are a data processing expert. Extract the seller/company name from this email.

EMAIL DETAILS:
Subject: {subject}
Sender Name: {sender_name}
Sender Email: {sender_email}
Body: {body_content[:2000]}  # First 2000 chars to avoid token limits

INSTRUCTIONS:
1. Identify the company/organization that is SENDING the loan data/tape
2. Look for company names in subject line, sender info, email signatures, or body text
3. Return ONLY the clean company name (no extra text, no explanations)
4. If multiple companies mentioned, return the one that is the DATA SENDER
5. Clean the name: remove "Inc", "LLC", "Corp", extra spaces, special characters
6. If no clear seller name found, return "UNKNOWN"

EXAMPLES:
- "SitusAMC Data Tape - October 2024" → "SitusAMC"
- "From: John Smith <john@abcservicing.com>" → "ABC Servicing"
- "Loan tape attached - Best regards, XYZ Capital" → "XYZ Capital"

Return only the seller name:"""

            client = anthropic.Anthropic(api_key=api_key)

            # Use Claude for intelligent name extraction
            message = client.messages.create(
                model="claude-3-5-haiku-20241022",  # Fast and cost-effective for simple text extraction
                max_tokens=100,  # Short response expected
                temperature=0,  # Deterministic output
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract text from response
            response_text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    response_text += block.text
                elif isinstance(block, dict) and 'text' in block:
                    response_text += block['text']

            extracted_name = response_text.strip()
            
            # Validate AI response
            if extracted_name and extracted_name.upper() != "UNKNOWN" and len(extracted_name) > 2:
                cleaned_name = self._clean_seller_name(extracted_name)
                if self.stdout:
                    self.stdout.write(f'   [AI-SELLER] AI extracted: "{cleaned_name}"\n')
                return cleaned_name

        except Exception as e:
            if self.stdout:
                self.stdout.write(f'   [AI-SELLER] AI extraction failed: {e}\n')
            logger.warning(f'AI seller name extraction failed: {e}')

        return None

    def _extract_from_filename(self, file_path: Path) -> Optional[str]:
        """
        WHAT: Extract seller name from filename using heuristic patterns
        WHY: Filenames often contain seller names (e.g., "SitusAMC_DataTape_Oct2024.xlsx")
        HOW: Use regex patterns to identify company names in filenames

        Args:
            file_path: Path to the data file

        Returns:
            Extracted seller name or None
        """
        filename = file_path.stem  # Filename without extension
        
        # Common filename patterns for seller names
        patterns = [
            r'^([A-Za-z][A-Za-z0-9\s&]+?)[-_\s]+(data|tape|loan|portfolio)',  # "SellerName_DataTape"
            r'^([A-Za-z][A-Za-z0-9\s&]+?)[-_\s]+\d{4}',  # "SellerName_2024"
            r'^([A-Za-z][A-Za-z0-9\s&]+?)[-_\s]+(oct|nov|dec|jan|feb|mar|apr|may|jun|jul|aug|sep)',  # "SellerName_Oct"
            r'^([A-Za-z][A-Za-z0-9\s&]{3,}?)[-_\s]',  # Generic: "SellerName_anything"
        ]

        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                cleaned = self._clean_seller_name(extracted)
                if len(cleaned) >= 3:  # Minimum reasonable seller name length
                    return cleaned

        return None

    def _extract_from_sender_domain(self, email_data: Dict[str, Any]) -> Optional[str]:
        """
        WHAT: Extract seller name from email sender domain
        WHY: Company domains often reflect company names (e.g., "john@situsamc.com" → "SitusAMC")
        HOW: Parse domain and convert to readable company name

        Args:
            email_data: Email metadata

        Returns:
            Extracted seller name or None
        """
        sender_email = email_data.get('from', {}).get('emailAddress', {}).get('address', '')
        
        if not sender_email or '@' not in sender_email:
            return None

        domain = sender_email.split('@')[1].lower()
        
        # Skip common email providers
        common_providers = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
            'aol.com', 'icloud.com', 'live.com', 'msn.com'
        }
        
        if domain in common_providers:
            return None

        # Extract company name from domain
        # Remove common suffixes and convert to title case
        domain_parts = domain.replace('.com', '').replace('.net', '').replace('.org', '').split('.')
        
        if domain_parts:
            company_name = domain_parts[0]
            # Convert to readable format (e.g., "situsamc" → "SitusAMC")
            if len(company_name) >= 3:
                return self._clean_seller_name(company_name.title())

        return None

    def _generate_fallback_name(
        self,
        email_data: Optional[Dict[str, Any]],
        file_path: Optional[Path]
    ) -> str:
        """
        WHAT: Generate fallback seller name when extraction fails
        WHY: Always need a seller name for database record creation
        HOW: Use timestamp + source info to create unique fallback name

        Args:
            email_data: Email metadata
            file_path: File path

        Returns:
            Generated fallback seller name
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        if email_data:
            sender_email = email_data.get('from', {}).get('emailAddress', {}).get('address', '')
            if sender_email:
                domain = sender_email.split('@')[1] if '@' in sender_email else 'unknown'
                return f"Unknown_Seller_{domain}_{timestamp}"
        
        if file_path:
            return f"Unknown_Seller_{file_path.stem[:20]}_{timestamp}"
        
        return f"Unknown_Seller_{timestamp}"

    def _clean_seller_name(self, name: str) -> str:
        """
        WHAT: Clean and intelligently format seller name with proper acronym handling
        WHY: Ensure consistent naming with proper capitalization (e.g., "SitusAMC" not "Situsamc")
        HOW: Use AI to identify acronyms and apply smart capitalization rules

        Args:
            name: Raw seller name

        Returns:
            Cleaned and properly formatted seller name
        """
        if not name:
            return ""
        
        # Basic cleaning
        cleaned = re.sub(r'\s+', ' ', name.strip())
        
        # Try AI-powered smart formatting first
        if os.getenv('ANTHROPIC_API_KEY'):
            ai_formatted = self._ai_format_seller_name(cleaned)
            if ai_formatted:
                return ai_formatted
        
        # Fallback to heuristic formatting
        return self._heuristic_format_seller_name(cleaned)

    def _ai_format_seller_name(self, name: str) -> Optional[str]:
        """
        WHAT: Use AI to intelligently format seller name with proper acronym handling
        WHY: AI can distinguish between words and acronyms better than regex
        HOW: Send name to Claude with specific formatting instructions

        Args:
            name: Raw seller name

        Returns:
            AI-formatted seller name or None if AI unavailable
        """
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                return None

            prompt = f"""Format this company name with proper capitalization and acronym handling.

COMPANY NAME: {name}

RULES:
1. Acronyms should be ALL CAPS (e.g., "AMC", "LLC", "REO", "NPL")
2. Regular words should be Title Case (e.g., "Capital", "Servicing", "Management")
3. Common acronyms: AMC, LLC, LLP, Inc, Corp, LP, REO, NPL, BPO, MSR, etc.
4. Keep spaces between words but remove extra spaces
5. No periods in acronyms unless part of official name

EXAMPLES:
- "situs amc" → "Situs AMC"
- "abc servicing llc" → "ABC Servicing LLC"
- "first national bank" → "First National Bank"
- "xyz capital management" → "XYZ Capital Management"
- "reo specialists inc" → "REO Specialists Inc"

Return only the formatted company name:"""

            client = anthropic.Anthropic(api_key=api_key)

            message = client.messages.create(
                model="claude-3-5-haiku-20241022",  # Fast for simple formatting
                max_tokens=50,  # Short response expected
                temperature=0,  # Deterministic output
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract response
            response_text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    response_text += block.text
                elif isinstance(block, dict) and 'text' in block:
                    response_text += block['text']

            formatted_name = response_text.strip().strip('"\'')
            
            if formatted_name and len(formatted_name) <= 100:  # Reasonable length
                if self.stdout:
                    self.stdout.write(f'   [AI-FORMAT] "{name}" → "{formatted_name}"\n')
                return formatted_name

        except Exception as e:
            if self.stdout:
                self.stdout.write(f'   [AI-FORMAT] Formatting failed: {e}\n')
            logger.warning(f'AI seller name formatting failed: {e}')

        return None

    def _heuristic_format_seller_name(self, name: str) -> str:
        """
        WHAT: Simple fallback formatting when AI unavailable
        WHY: Basic title case is better than nothing
        HOW: Just use title case - simple and reliable

        Args:
            name: Raw seller name

        Returns:
            Title-cased seller name
        """
        return name.title()

    def _find_matching_seller(self, seller_name: str) -> Optional[Seller]:
        """
        WHAT: Find existing seller using fuzzy string matching
        WHY: Seller names might have slight variations (e.g., "SitusAMC" vs "Situs AMC")
        HOW: Use SequenceMatcher to find best similarity match above threshold

        Args:
            seller_name: Cleaned seller name to match

        Returns:
            Matching Seller instance or None
        """
        # Load all sellers into cache if not already loaded
        if not self._seller_cache:
            self._load_seller_cache()

        if not self._seller_cache:
            return None  # No existing sellers

        best_match = None
        best_score = 0.0

        # Compare against all existing seller names
        for seller_id, existing_name in self._seller_cache.items():
            # Calculate similarity score
            similarity = SequenceMatcher(None, seller_name.lower(), existing_name.lower()).ratio()
            
            if similarity > best_score and similarity >= self.similarity_threshold:
                best_score = similarity
                best_match = seller_id

        if best_match:
            seller = Seller.objects.get(id=best_match)
            if self.stdout:
                self.stdout.write(f'   [AI-SELLER] Fuzzy match: "{seller_name}" -> "{seller.name}" (score: {best_score:.2f})\n')
            return seller

        return None

    def _load_seller_cache(self):
        """
        WHAT: Load all existing sellers into memory cache for fast matching
        WHY: Avoid repeated database queries during fuzzy matching
        HOW: Query all sellers and store id → name mapping
        """
        try:
            sellers = Seller.objects.all().values('id', 'name')
            self._seller_cache = {seller['id']: seller['name'] for seller in sellers}
            
            if self.stdout and self._seller_cache:
                self.stdout.write(f'   [AI-SELLER] Loaded {len(self._seller_cache)} existing sellers for matching\n')
                
        except Exception as e:
            logger.warning(f'Failed to load seller cache: {e}')
            self._seller_cache = {}

    def _create_new_seller(self, seller_name: str, email_data: Optional[Dict[str, Any]] = None) -> Seller:
        """
        WHAT: Create new Seller record in database
        WHY: When no existing seller matches, create a new one
        HOW: Use Django ORM to create Seller with extracted name and email info

        Args:
            seller_name: Cleaned seller name
            email_data: Email metadata for additional fields (optional)

        Returns:
            Newly created Seller instance
        """
        # Extract additional info from email if available
        email = None
        poc = None
        
        if email_data:
            sender_info = email_data.get('from', {}).get('emailAddress', {})
            email = sender_info.get('address')
            poc = sender_info.get('name')

        try:
            with transaction.atomic():
                # Create new seller record
                seller = Seller.objects.create(
                    name=seller_name,
                    email=email,
                    poc=poc,
                    # broker field left blank - can be filled manually later
                )
                
                # Update cache with new seller
                self._seller_cache[seller.id] = seller.name
                
                return seller
                
        except Exception as e:
            logger.error(f'Failed to create new seller "{seller_name}": {e}')
            raise

    def get_similarity_score(self, name1: str, name2: str) -> float:
        """
        WHAT: Calculate similarity score between two seller names
        WHY: Useful for debugging and manual verification
        HOW: Use SequenceMatcher ratio calculation

        Args:
            name1: First seller name
            name2: Second seller name

        Returns:
            Similarity score between 0.0 and 1.0
        """
        return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()

    def list_potential_matches(self, seller_name: str, limit: int = 5) -> List[Tuple[Seller, float]]:
        """
        WHAT: Get list of potential seller matches with similarity scores
        WHY: Useful for manual review and debugging
        HOW: Return top N matches sorted by similarity score

        Args:
            seller_name: Seller name to match
            limit: Maximum number of matches to return

        Returns:
            List of (Seller, similarity_score) tuples
        """
        if not self._seller_cache:
            self._load_seller_cache()

        matches = []
        
        for seller_id, existing_name in self._seller_cache.items():
            similarity = self.get_similarity_score(seller_name, existing_name)
            if similarity > 0.1:  # Only include reasonable matches
                seller = Seller.objects.get(id=seller_id)
                matches.append((seller, similarity))

        # Sort by similarity score (highest first) and limit results
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:limit]

    def generate_trade_name(
        self,
        seller: Seller,
        email_data: Optional[Dict[str, Any]] = None,
        file_path: Optional[Path] = None
    ) -> str:
        """
        WHAT: Generate simple trade name in format: SellerName[TapeID] - MM.DD.YY[-sequence]
        WHY: Simple, consistent naming that includes seller, tape ID, and date
        HOW: Extract tape ID with AI, combine with seller name and date

        Args:
            seller: Seller instance
            email_data: Email metadata for context (optional)
            file_path: File path for context (optional)

        Returns:
            Generated trade name string in format: "SitusAMC20791 - 10.28.25" or "SitusAMC - 10.28.25"
        """
        from datetime import datetime
        
        # Get current date in MM.DD.YY format
        date_str = datetime.now().strftime('%m.%d.%y')
        
        # Clean seller name using smart formatting, then remove spaces for trade name
        seller_formatted = self._clean_seller_name(seller.name)
        seller_clean = re.sub(r'[^A-Za-z0-9]', '', seller_formatted)  # Remove spaces and special chars
        
        # Try to extract tape ID using AI
        tape_id = None
        if email_data and os.getenv('ANTHROPIC_API_KEY'):
            tape_id = self._ai_extract_tape_id(email_data, file_path)
        
        # If no AI tape ID, try heuristic extraction
        if not tape_id:
            tape_id = self._heuristic_extract_tape_id(email_data, file_path)
        
        # Build base trade name
        if tape_id:
            base_name = f"{seller_clean}{tape_id} - {date_str}"
        else:
            base_name = f"{seller_clean} - {date_str}"
        
        # Ensure uniqueness with sequence number
        return self._ensure_unique_trade_name_simple(seller, base_name, date_str)

    def _ai_extract_tape_id(self, email_data: Dict[str, Any], file_path: Optional[Path] = None) -> Optional[str]:
        """
        WHAT: Use AI to extract tape/batch ID from email content or filename
        WHY: Many sellers include specific tape IDs that should be part of trade name
        HOW: Send context to Claude to identify numeric/alphanumeric identifiers

        Args:
            email_data: Email metadata
            file_path: File path (optional)

        Returns:
            Extracted tape ID or None
        """
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                return None

            # Prepare context for AI
            subject = email_data.get('subject', '')
            body_content = email_data.get('body', {}).get('content', '')[:500]  # First 500 chars
            filename = file_path.name if file_path else ''
            
            # Create AI prompt for tape ID extraction
            prompt = f"""Extract the tape/batch ID from this loan data email.

CONTEXT:
Email Subject: {subject}
Filename: {filename}
Email Body: {body_content}

INSTRUCTIONS:
1. Look for numeric or alphanumeric identifiers that represent a tape/batch ID
2. Common patterns: "20791", "Tape123", "Batch456", "ID789", etc.
3. Usually 3-8 characters, often numeric
4. Ignore dates, years, months - focus on tape/batch identifiers
5. If multiple IDs found, return the most likely tape identifier
6. If no clear tape ID found, return "NONE"

EXAMPLES:
- "SitusAMC Data Tape 20791" → "20791"
- "Batch ID: ABC123 for October" → "ABC123"
- "Monthly portfolio data" → "NONE"

Return only the tape ID or "NONE":"""

            client = anthropic.Anthropic(api_key=api_key)

            message = client.messages.create(
                model="claude-3-5-haiku-20241022",  # Fast for simple extraction
                max_tokens=20,  # Very short response expected
                temperature=0,  # Deterministic output
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract response
            response_text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    response_text += block.text
                elif isinstance(block, dict) and 'text' in block:
                    response_text += block['text']

            tape_id = response_text.strip().strip('"\'')
            
            # Validate response
            if tape_id and tape_id.upper() != "NONE" and len(tape_id) <= 20:
                if self.stdout:
                    self.stdout.write(f'   [AI-TAPE-ID] Extracted: "{tape_id}"\n')
                return tape_id

        except Exception as e:
            if self.stdout:
                self.stdout.write(f'   [AI-TAPE-ID] Extraction failed: {e}\n')
            logger.warning(f'AI tape ID extraction failed: {e}')

        return None

    def _heuristic_extract_tape_id(
        self,
        email_data: Optional[Dict[str, Any]] = None,
        file_path: Optional[Path] = None
    ) -> Optional[str]:
        """
        WHAT: Extract tape ID using heuristic patterns (fallback when AI unavailable)
        WHY: Still want to capture tape IDs even without AI
        HOW: Use regex patterns to find likely tape identifiers

        Args:
            email_data: Email metadata (optional)
            file_path: File path (optional)

        Returns:
            Extracted tape ID or None
        """
        # Combine all text sources
        text_sources = []
        
        if email_data:
            subject = email_data.get('subject', '')
            body = email_data.get('body', {}).get('content', '')
            text_sources.extend([subject, body])
        
        if file_path:
            text_sources.append(file_path.stem)
        
        combined_text = ' '.join(text_sources)
        
        # Common tape ID patterns
        patterns = [
            r'\b(\d{4,8})\b',  # 4-8 digit numbers (most common)
            r'tape\s*[#:]?\s*([A-Za-z0-9]{3,8})',  # "Tape 123" or "Tape: ABC123"
            r'batch\s*[#:]?\s*([A-Za-z0-9]{3,8})',  # "Batch 456"
            r'id\s*[#:]?\s*([A-Za-z0-9]{3,8})',  # "ID: 789"
            r'\b([A-Z]{2,4}\d{3,6})\b',  # Mixed alpha-numeric like "ABC123"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            if matches:
                # Return first match that looks like a tape ID
                for match in matches:
                    # Skip obvious dates (years, months)
                    if not re.match(r'^(19|20)\d{2}$', match) and not match in ['2024', '2025']:
                        return match
        
        return None

    def _heuristic_generate_trade_name(
        self,
        seller: Seller,
        email_data: Optional[Dict[str, Any]] = None,
        file_path: Optional[Path] = None
    ) -> str:
        """
        WHAT: Generate simple trade name as fallback (should not be called with new logic)
        WHY: Maintain backward compatibility
        HOW: Use the same simple format as main method

        Args:
            seller: Seller instance
            email_data: Email metadata (optional)
            file_path: File path (optional)

        Returns:
            Generated trade name in simple format
        """
        # This method is now just a wrapper - main logic moved to generate_trade_name
        return self.generate_trade_name(seller, email_data, file_path)

    def _ensure_unique_trade_name_simple(self, seller: Seller, base_name: str, date_str: str) -> str:
        """
        WHAT: Ensure trade name is unique using simple sequence format
        WHY: Handle multiple trades on same day with -2, -3, etc.
        HOW: Check existing trades for same date and add sequence number

        Args:
            seller: Seller instance
            base_name: Base trade name (e.g., "SitusAMC20791 - 10.28.25")
            date_str: Date string (e.g., "10.28.25")

        Returns:
            Unique trade name (e.g., "SitusAMC20791 - 10.28.25-2")
        """
        # Check if base name is already unique
        if not Trade.objects.filter(seller=seller, trade_name=base_name).exists():
            return base_name

        # Find next available sequence number for this date
        sequence = 2
        while True:
            candidate_name = f"{base_name}-{sequence}"
            if not Trade.objects.filter(seller=seller, trade_name=candidate_name).exists():
                return candidate_name
            sequence += 1
            
            # Safety valve to prevent infinite loop
            if sequence > 999:
                # Use timestamp as last resort
                from datetime import datetime
                timestamp = datetime.now().strftime('%H%M')
                return f"{base_name}-{timestamp}"

    def _ensure_unique_trade_name(self, seller: Seller, base_name: str) -> str:
        """
        WHAT: Ensure trade name is unique by adding sequence number if needed
        WHY: Avoid database constraint violations for duplicate trade names
        HOW: Check existing trades and append sequence number

        Args:
            seller: Seller instance
            base_name: Base trade name

        Returns:
            Unique trade name
        """
        # Truncate base name to leave room for sequence number
        max_base_length = 90  # Leave room for " - 999"
        if len(base_name) > max_base_length:
            base_name = base_name[:max_base_length].strip()

        # Check if base name is already unique
        if not Trade.objects.filter(seller=seller, trade_name=base_name).exists():
            return base_name

        # Find next available sequence number
        sequence = 2
        while True:
            candidate_name = f"{base_name} - {sequence}"
            if not Trade.objects.filter(seller=seller, trade_name=candidate_name).exists():
                return candidate_name
            sequence += 1
            
            # Safety valve to prevent infinite loop
            if sequence > 999:
                # Use timestamp as last resort
                from datetime import datetime
                timestamp = datetime.now().strftime('%H%M%S')
                return f"{base_name[:80]} - {timestamp}"
