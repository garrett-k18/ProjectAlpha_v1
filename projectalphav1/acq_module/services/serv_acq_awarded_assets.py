"""
Awarded Assets Service

WHAT: Handles AI-powered extraction of awarded asset IDs from spreadsheets/PDFs and bulk status updates
WHY: Users need to drop non-awarded assets after winning bids
HOW: Use Claude Haiku 3.5 to extract IDs from spreadsheet files (text API) and PDFs (vision API), match against DB

USAGE:
    service = AwardedAssetsService(trade_id=123)
    result = service.extract_ids_from_file(file_bytes, filename, mime_type)
    preview = service.preview_drop(awarded_ids)
    service.execute_drop(awarded_ids, user)

Docs reviewed:
- Claude API: https://docs.anthropic.com/claude/reference/messages_post
- Django QuerySet: https://docs.djangoproject.com/en/5.2/ref/models/querysets/
"""

import logging
import json
import io
import os
import pandas as pd
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from acq_module.models.model_acq_seller import Trade, AcqAsset
from etl.services.services_valuationExtract.serv_etl_claude_client import (
    build_valuation_claude_vision_client
)

# WHAT: Import Anthropic for direct API calls
# WHY: Use Claude text API to extract IDs from spreadsheet data, vision API for PDFs
try:
    import anthropic
except Exception:
    anthropic = None

logger = logging.getLogger(__name__)
User = get_user_model()


class AwardedAssetsService:
    """
    WHAT: Service for processing awarded assets and dropping non-awarded
    WHY: Centralize business logic for awarded assets workflow
    HOW: AI extraction → matching → preview → execute
    """

    def __init__(self, trade_id: int):
        """
        Initialize service for a specific trade
        
        Args:
            trade_id: ID of the trade to process
        """
        # WHAT: Get trade and validate it exists
        # WHY: All operations are scoped to a single trade
        # HOW: Use select_related to prefetch seller
        self.trade = Trade.objects.select_related('seller').get(pk=trade_id)
        self.trade_id = trade_id
        
        # WHAT: Initialize Claude vision client for PDF extraction
        # WHY: PDFs with tables across pages need vision API to read
        # HOW: Use existing ETL Claude vision client
        self.claude_vision_client = build_valuation_claude_vision_client(
            default_model="claude-3-5-haiku-20241022",
            max_tokens=4096
        )
        
        # WHAT: Initialize Anthropic client for spreadsheet extraction
        # WHY: Use Claude text API to extract IDs from spreadsheet data
        # HOW: Create Anthropic client if API key available
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key and anthropic:
            self.claude_client = anthropic.Anthropic(api_key=api_key)
            self.default_model = "claude-3-5-haiku-20241022"
        else:
            self.claude_client = None
            logger.warning("ANTHROPIC_API_KEY not set or anthropic package unavailable - spreadsheet extraction disabled")
        
        if not self.claude_vision_client and not self.claude_client:
            logger.error("Claude client initialization failed - check ANTHROPIC_API_KEY")

    def extract_ids_from_file(
        self, 
        file_bytes: bytes, 
        filename: str,
        mime_type: str
    ) -> Dict[str, Any]:
        """
        WHAT: Extract asset IDs from uploaded spreadsheet or PDF file using Claude AI
        WHY: Handle Excel/CSV files and PDFs (with tables across pages) without manual parsing
        HOW: Route to text API for spreadsheets, vision API for PDFs, parse JSON response
        
        Args:
            file_bytes: Raw file content
            filename: Original filename (should be .xlsx, .xls, .csv, or .pdf)
            mime_type: MIME type (e.g., 'application/pdf', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            
        Returns:
            {
                'identifiers': ['ABC123', 'DEF456', ...],
                'confidence': 'high|medium|low',
                'detected_format': 'description',
                'raw_response': 'full AI response',
                'error': 'error message if failed'
            }
        """
        # WHAT: Validate Claude client is available
        # WHY: Can't extract without AI
        if not self.claude_client and not self.claude_vision_client:
            return {
                'identifiers': [],
                'confidence': 'none',
                'error': 'Claude AI client not available - check ANTHROPIC_API_KEY'
            }
        
        # WHAT: Determine file type and validate
        # WHY: Route to appropriate API based on file type
        # HOW: Check file extension and MIME type
        is_spreadsheet = filename.endswith(('.xlsx', '.xls', '.csv'))
        is_pdf = filename.endswith('.pdf') or 'pdf' in mime_type.lower()
        
        if not is_spreadsheet and not is_pdf:
            return {
                'identifiers': [],
                'confidence': 'none',
                'error': f'Unsupported file type: {filename}. Only Excel (.xlsx, .xls), CSV (.csv), and PDF (.pdf) files are supported.'
            }
        
        # WHAT: Build extraction prompt
        # WHY: Tell Claude exactly what to look for and how to format response
        # HOW: Structured prompt with JSON schema
        prompt = self._build_extraction_prompt(filename, is_pdf=is_pdf)
        
        try:
            if is_spreadsheet:
                logger.info(f"Processing spreadsheet: {filename} ({len(file_bytes)} bytes) for trade {self.trade_id}")
                
                if not self.claude_client:
                    return {
                        'identifiers': [],
                        'confidence': 'none',
                        'error': 'Claude text client not available for spreadsheet extraction'
                    }
                
                # WHAT: Convert spreadsheet to text
                # WHY: Send data to Claude as text for AI analysis
                # HOW: Use pandas to read then convert to CSV string representation
                text_data = self._convert_spreadsheet_to_text(file_bytes, filename)
                
                # WHAT: Append spreadsheet data to prompt
                # WHY: Give Claude the actual data to analyze
                # HOW: Concatenate prompt with data
                full_prompt = f"{prompt}\n\nDOCUMENT DATA:\n{text_data}"
                
                # WHAT: Extract IDs using Claude text API
                # WHY: AI can find IDs even if format varies
                # HOW: Call custom text extraction method
                response = self._extract_ids_from_text(full_prompt)
            
            elif is_pdf:
                logger.info(f"Processing PDF: {filename} ({len(file_bytes)} bytes) for trade {self.trade_id}")
                
                if not self.claude_vision_client:
                    return {
                        'identifiers': [],
                        'confidence': 'none',
                        'error': 'Claude vision client not available for PDF extraction'
                    }
                
                # WHAT: Extract IDs using Claude Vision API
                # WHY: PDFs with tables across pages need vision to read all pages
                # HOW: Send PDF directly to vision API
                response = self.claude_vision_client(
                    file_bytes=file_bytes,
                    mime_type='application/pdf',
                    prompt=prompt
                )
            
            # WHAT: Parse and validate response
            # WHY: Ensure we got structured data
            # HOW: Check for required fields
            if not response:
                logger.warning(f"Claude returned empty response for {filename}")
                return {
                    'identifiers': [],
                    'confidence': 'none',
                    'error': 'Claude returned empty response - check logs for details'
                }
            
            # WHAT: Extract identifiers from response
            # WHY: Claude may return nested structure
            # HOW: Handle various response formats
            identifiers = response.get('identifiers', [])
            if not identifiers and 'ids' in response:
                identifiers = response['ids']
            if not identifiers and 'asset_ids' in response:
                identifiers = response['asset_ids']
            
            # WHAT: Ensure identifiers is a list
            # WHY: Handle edge cases where response structure is unexpected
            # HOW: Convert to list if needed, default to empty list
            if not isinstance(identifiers, list):
                logger.warning(f"Identifiers from Claude is not a list for {filename}: {type(identifiers)}")
                identifiers = []
            
            # WHAT: Clean and deduplicate identifiers
            # WHY: Remove empty strings, whitespace, duplicates
            # HOW: Strip, filter, convert to set then list
            identifiers = list(set([
                str(id_val).strip() 
                for id_val in identifiers 
                if id_val and str(id_val).strip()
            ]))
            
            logger.info(f"Extracted {len(identifiers)} unique IDs from {filename}")
            
            return {
                'identifiers': identifiers,
                'confidence': response.get('confidence', 'medium'),
                'detected_format': response.get('detected_format', 'Unknown format'),
                'raw_response': json.dumps(response, indent=2),
                'count': len(identifiers)
            }
            
        except Exception as e:
            logger.error(f"Failed to extract IDs from {filename}: {str(e)}", exc_info=True)
            return {
                'identifiers': [],
                'confidence': 'none',
                'error': f'Extraction failed: {str(e)}'
            }

    def _convert_spreadsheet_to_text(self, file_bytes: bytes, filename: str) -> str:
        """
        WHAT: Convert spreadsheet bytes to a text representation for Claude
        WHY: Claude text API needs data as text to analyze and extract IDs
        HOW: Use pandas to read the file and convert to CSV string format
        """
        try:
            file_io = io.BytesIO(file_bytes)
            
            if filename.endswith('.csv'):
                df = pd.read_csv(file_io)
            else:
                # Handle Excel (.xlsx, .xls)
                # We read only the first sheet for now to keep it simple and within token limits
                df = pd.read_excel(file_io)
            
            # WHAT: Limit data size
            # WHY: Token limits and cost
            # HOW: Take first 1000 rows if it's huge, but usually award lists are small
            if len(df) > 1000:
                logger.warning(f"Spreadsheet {filename} has {len(df)} rows. Limiting to first 1000 for extraction.")
                df = df.head(1000)
            
            # Convert to string (CSV format is very efficient for tokens)
            return df.to_csv(index=False)
            
        except Exception as e:
            logger.error(f"Error converting spreadsheet to text: {str(e)}")
            return f"[Error parsing spreadsheet: {str(e)}]"

    def _extract_ids_from_text(self, prompt: str) -> Dict[str, Any]:
        """
        WHAT: Extract identifiers from text using Claude text API
        WHY: Custom method for spreadsheet extraction that handles JSON response correctly
        HOW: Direct call to Anthropic API, parse JSON response
        
        Args:
            prompt: Full prompt with spreadsheet data embedded
            
        Returns:
            Dict with 'identifiers', 'confidence', 'detected_format' keys
        """
        if not self.claude_client:
            logger.error("Anthropic client not initialized for text extraction")
            return {}
        
        try:
            # WHAT: Call Claude API directly
            # WHY: Need full control over response parsing (not valuation-specific format)
            # HOW: Use Anthropic client messages.create
            message = self.claude_client.messages.create(
                model=self.default_model,
                max_tokens=4096,
                temperature=0,
                system=(
                    "You are extracting structured data from documents. "
                    "Return ONLY valid JSON with the requested structure."
                ),
                messages=[{"role": "user", "content": prompt}],
            )
            
            # WHAT: Extract response text
            # WHY: Claude returns content blocks
            # HOW: Iterate through content blocks and concatenate text
            response_text = ""
            for block in getattr(message, "content", []):
                if isinstance(block, dict):
                    response_text += str(block.get("text", ""))
                else:
                    response_text += getattr(block, "text", "")
            
            # WHAT: Parse JSON from response
            # WHY: Claude may wrap JSON in markdown code blocks
            # HOW: Strip markdown formatting if present, then parse JSON
            response_text = (response_text or "").strip()
            if not response_text:
                logger.warning("Claude returned empty response for text extraction")
                return {}
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
            
            # WHAT: Parse JSON payload
            # WHY: Extract structured data from Claude's response
            # HOW: Try to parse as JSON, handle multiple JSON objects if present
            try:
                # Try parsing the full response
                payload = json.loads(response_text)
            except json.JSONDecodeError:
                # WHAT: Try to extract JSON from mixed text
                # WHY: Claude sometimes adds explanatory text around JSON
                # HOW: Look for JSON-like structures
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}")
                if start_idx >= 0 and end_idx > start_idx:
                    try:
                        payload = json.loads(response_text[start_idx:end_idx+1])
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse JSON from Claude response: {response_text[:200]}")
                        return {}
                else:
                    logger.error(f"No JSON structure found in Claude response: {response_text[:200]}")
                    return {}
            
            # WHAT: Validate payload structure
            # WHY: Ensure we have the expected keys
            # HOW: Check if it's a dict with expected structure
            if isinstance(payload, dict) and payload:
                logger.info(f"Successfully extracted JSON response from Claude: {list(payload.keys())}")
                return payload
            else:
                logger.warning(f"Claude returned invalid payload structure: {type(payload)}")
                return {}
                
        except Exception as exc:
            logger.error(f"Failed to extract IDs from text using Claude: {str(exc)}", exc_info=True)
            return {}

    def preview_drop(self, awarded_ids: List[str]) -> Dict[str, Any]:
        """
        WHAT: Preview which assets will be kept/dropped without executing
        WHY: User needs to review before confirming destructive action
        HOW: Match IDs against DB, categorize results
        
        Args:
            awarded_ids: List of asset IDs from uploaded file
            
        Returns:
            {
                'matched_assets': [...],      # Assets that will be KEPT
                'unmatched_ids': [...],       # IDs from file not found in DB
                'will_be_dropped': [...],     # Assets that will be DROPPED
                'summary': {
                    'total_in_trade': 500,
                    'matched_from_file': 250,
                    'will_keep': 250,
                    'will_drop': 250,
                    'unmatched_from_file': 5
                }
            }
        """
        # WHAT: Get all assets for this trade
        # WHY: Need to categorize into keep/drop
        # HOW: Query SellerRawData filtered by trade
        all_assets = AcqAsset.objects.filter(
            trade=self.trade
        ).select_related('asset_hub', 'loan', 'property')
        
        total_count = all_assets.count()
        
        # WHAT: Try to match awarded IDs against various ID fields
        # WHY: Files may contain different ID formats
        # HOW: Check sellertape_id, sellertape_altid, asset_hub.sellertape_id
        matched_assets = []
        matched_ids = set()
        
        for asset in all_assets:
            # WHAT: Build list of all possible IDs for this asset
            # WHY: Match against any ID field
            # HOW: Collect non-null IDs from SellerRawData and AssetIdHub
            loan = getattr(asset, 'loan', None)
            asset_ids = [
                str(loan.sellertape_id).strip() if loan and loan.sellertape_id else None,
                str(loan.sellertape_altid).strip() if loan and loan.sellertape_altid else None,
            ]
            
            # WHAT: Add asset_hub sellertape_id if available
            # WHY: AssetIdHub also has a sellertape_id field that might match
            # HOW: Check if asset_hub exists and has sellertape_id
            if asset.asset_hub and asset.asset_hub.sellertape_id:
                asset_ids.append(str(asset.asset_hub.sellertape_id).strip())
            
            # WHAT: Remove None values and empty strings
            # WHY: Clean list before matching
            # HOW: Filter out None and empty values
            asset_ids = [aid for aid in asset_ids if aid]
            
            # WHAT: Check if any of this asset's IDs match awarded list
            # WHY: Determine if asset should be kept
            # HOW: Set intersection
            if any(aid in awarded_ids for aid in asset_ids):
                matched_assets.append({
                    'id': asset.pk,  # WHAT: Use pk since asset_hub is the primary key (no separate id field)
                    'sellertape_id': loan.sellertape_id if loan else None,
                    'street_address': asset.property.street_address if asset.property and asset.property.street_address else '',
                    'city': asset.property.city if asset.property and asset.property.city else '',
                    'state': asset.property.state if asset.property and asset.property.state else '',
                    'current_balance': float(asset.loan.current_balance) if asset.loan and asset.loan.current_balance else 0,
                    'acquisition_status': asset.acq_status,
                    'matched_on': next((aid for aid in asset_ids if aid in awarded_ids), None)
                })
                matched_ids.add(asset.pk)  # WHAT: Use pk since asset_hub is the primary key
        
        # WHAT: Find assets that will be dropped
        # WHY: Show user what will be removed
        # HOW: All assets NOT in matched set
        will_be_dropped = []
        for asset in all_assets:
            if asset.pk not in matched_ids:  # WHAT: Use pk since asset_hub is the primary key
                loan = getattr(asset, 'loan', None)
                will_be_dropped.append({
                    'id': asset.pk,  # WHAT: Use pk since asset_hub is the primary key (no separate id field)
                    'sellertape_id': loan.sellertape_id if loan else None,
                    'street_address': asset.property.street_address if asset.property and asset.property.street_address else '',
                    'city': asset.property.city if asset.property and asset.property.city else '',
                    'state': asset.property.state if asset.property and asset.property.state else '',
                    'current_balance': float(asset.loan.current_balance) if asset.loan and asset.loan.current_balance else 0,
                    'acquisition_status': asset.acq_status
                })
        
        # WHAT: Find IDs from file that didn't match any assets
        # WHY: Alert user to potential issues
        # HOW: Set difference
        matched_id_strings = set()
        for asset_dict in matched_assets:
            matched_id_strings.add(asset_dict['matched_on'])
        
        unmatched_ids = [aid for aid in awarded_ids if aid not in matched_id_strings]
        
        # WHAT: Build summary statistics
        # WHY: Give user overview before confirming
        summary = {
            'total_in_trade': total_count,
            'matched_from_file': len(matched_assets),
            'will_keep': len(matched_assets),
            'will_drop': len(will_be_dropped),
            'unmatched_from_file': len(unmatched_ids)
        }
        
        logger.info(
            f"Preview for trade {self.trade_id}: "
            f"{summary['will_keep']} keep, {summary['will_drop']} drop, "
            f"{summary['unmatched_from_file']} unmatched"
        )
        
        return {
            'matched_assets': matched_assets,
            'will_be_dropped': will_be_dropped,
            'unmatched_ids': unmatched_ids,
            'summary': summary,
            'trade_name': self.trade.trade_name,
            'trade_id': self.trade_id
        }

    @transaction.atomic
    def execute_drop(
        self, 
        awarded_ids: List[str], 
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """
        WHAT: Execute the drop by setting acquisition_status='DROP' for non-awarded
        WHY: Remove unwanted assets from active pool after bid award
        HOW: Update SellerRawData records in transaction
        
        Args:
            awarded_ids: List of asset IDs to KEEP
            user: User executing the drop (for audit trail)
            
        Returns:
            {
                'success': True,
                'kept_count': 250,
                'dropped_count': 250,
                'dropped_ids': [1, 2, 3, ...],
                'message': 'Successfully processed...'
            }
        """
        # WHAT: Get preview to determine which assets to drop
        # WHY: Reuse matching logic
        # HOW: Call preview_drop
        preview = self.preview_drop(awarded_ids)
        
        dropped_ids = [asset['id'] for asset in preview['will_be_dropped']]
        
        if not dropped_ids:
            logger.info(f"No assets to drop for trade {self.trade_id}")
            return {
                'success': True,
                'kept_count': preview['summary']['will_keep'],
                'dropped_count': 0,
                'dropped_ids': [],
                'message': 'No assets to drop - all assets are awarded'
            }
        
        # WHAT: Update acquisition_status to DROP for non-awarded assets
        # WHY: Soft delete - can be undone
        # HOW: Bulk update with filter using pk since asset_hub is the primary key
        updated_count = AcqAsset.objects.filter(
            pk__in=dropped_ids  # WHAT: Use pk__in since asset_hub is the primary key (no separate id field)
        ).update(
            acq_status=AcqAsset.AcquisitionStatus.DROP,
            updated_at=timezone.now()
        )
        
        logger.info(
            f"Dropped {updated_count} assets for trade {self.trade_id} "
            f"(user: {user.username if user else 'system'})"
        )
        
        # TODO: Add audit log entry when audit model is created
        # AuditLog.objects.create(
        #     trade=self.trade,
        #     action='DROP_NON_AWARDED',
        #     user=user,
        #     details={'dropped_count': updated_count, 'dropped_ids': dropped_ids}
        # )
        
        return {
            'success': True,
            'kept_count': preview['summary']['will_keep'],
            'dropped_count': updated_count,
            'dropped_ids': dropped_ids,
            'message': f'Successfully dropped {updated_count} non-awarded assets. {preview["summary"]["will_keep"]} assets kept.'
        }

    @transaction.atomic
    def undo_drop(self, asset_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        WHAT: Restore dropped assets by setting acquisition_status back to KEEP
        WHY: Allow users to undo mistakes
        HOW: Update SellerRawData records
        
        Args:
            asset_ids: Specific asset IDs to restore, or None for all dropped in trade
            
        Returns:
            {
                'success': True,
                'restored_count': 50,
                'message': 'Successfully restored...'
            }
        """
        # WHAT: Build query for dropped assets
        # WHY: Find assets to restore
        # HOW: Filter by trade and DROP status
        query = AcqAsset.objects.filter(
            trade=self.trade,
            acq_status=AcqAsset.AcquisitionStatus.DROP
        )
        
        # WHAT: Optionally filter to specific asset IDs
        # WHY: User may want to restore only some assets
        # HOW: Use pk__in since asset_hub is the primary key (no separate id field)
        if asset_ids:
            query = query.filter(pk__in=asset_ids)
        
        # WHAT: Update status back to KEEP
        # WHY: Restore assets to active pool
        # HOW: Bulk update
        restored_count = query.update(
            acq_status=AcqAsset.AcquisitionStatus.KEEP,
            updated_at=timezone.now()
        )
        
        logger.info(f"Restored {restored_count} assets for trade {self.trade_id}")
        
        return {
            'success': True,
            'restored_count': restored_count,
            'message': f'Successfully restored {restored_count} assets to KEEP status'
        }

    def _build_extraction_prompt(self, filename: str, is_pdf: bool = False) -> str:
        """
        WHAT: Build structured prompt for Claude to extract asset IDs
        WHY: Get consistent JSON response from AI
        HOW: Template with clear instructions and examples
        
        Args:
            filename: Name of uploaded file (for context)
            is_pdf: Whether the file is a PDF (True) or spreadsheet (False)

        Returns:
            Formatted prompt string
        """
        if is_pdf:
            # WHAT: Prompt for PDF files with tables across pages
            # WHY: PDFs may have tables spanning multiple pages that need careful extraction
            # HOW: Provide specific instructions for PDF table extraction
            return f"""You are analyzing a PDF document titled "{filename}" that contains a list of awarded asset IDs.

Your task is to extract ALL asset/loan identifiers from this PDF document.

These identifiers may appear as:
- Loan IDs
- Seller Tape IDs
- Asset IDs
- Account Numbers
- Any alphanumeric identifiers in tables, columns, or rows

IMPORTANT - PDF Table Handling:
- The PDF may contain tables that span across multiple pages
- Extract identifiers from ALL pages of the document
- If a table continues across pages, extract IDs from both the continuation and new pages
- Look for table headers (like "Loan ID", "Asset ID", "Tape ID") and extract all values from those columns
- IDs may be in any column - scan all columns carefully
- Ignore headers, footers, page numbers, and document metadata
- Extract identifiers even if they're split across page breaks

IMPORTANT:
- Extract EVERY identifier you find, even if there are thousands
- Include the full identifier exactly as shown (preserve leading zeros, dashes, etc.)
- Be thorough - check every page and every table
- If tables repeat headers on new pages, extract all data rows, not just the headers

Return your response as valid JSON with this exact structure:
{{
  "identifiers": ["ABC123", "DEF456", "GHI789", ...],
  "confidence": "high|medium|low",
  "detected_format": "Brief description of what you found (e.g., 'PDF with table spanning 5 pages, Loan ID column found starting on page 2')"
}}

If you cannot find any identifiers, return:
{{
  "identifiers": [],
  "confidence": "none",
  "detected_format": "No identifiers found in document"
}}"""
        else:
            # WHAT: Prompt for spreadsheet files
            # WHY: Spreadsheets are provided as text data, need specific instructions
            # HOW: Provide instructions for CSV/text format data
            return f"""You are analyzing a spreadsheet file titled "{filename}" that contains a list of awarded asset IDs.

Your task is to extract ALL asset/loan identifiers from this spreadsheet.

These identifiers may appear as:
- Loan IDs
- Seller Tape IDs
- Asset IDs
- Account Numbers
- Any alphanumeric identifiers in columns or rows

The spreadsheet data is provided below. The data may:
- Start at any row (not necessarily row 1)
- Have headers in various formats
- Contain multiple columns with IDs in different formats
- Have empty rows or cells mixed in

IMPORTANT:
- Extract EVERY identifier you find, even if there are thousands
- Include the full identifier exactly as shown (preserve leading zeros, dashes, etc.)
- If you see column headers like "Loan ID", "Asset ID", "Tape ID", extract all values from that column
- Ignore empty cells and rows
- Look across ALL columns - IDs might be in any column

Return your response as valid JSON with this exact structure:
{{
  "identifiers": ["ABC123", "DEF456", "GHI789", ...],
  "confidence": "high|medium|low",
  "detected_format": "Brief description of what you found (e.g., 'Excel spreadsheet with Loan ID column starting at row 5')"
}}

If you cannot find any identifiers, return:
{{
  "identifiers": [],
  "confidence": "none",
  "detected_format": "No identifiers found in document"
}}"""

    def get_drop_history(self) -> Dict[str, Any]:
        """
        WHAT: Get history of dropped assets for this trade
        WHY: Show user what was dropped and when
        HOW: Query SellerRawData with DROP status
        
        Returns:
            {
                'dropped_assets': [...],
                'dropped_count': 50,
                'kept_count': 250
            }
        """
        # WHAT: Get all dropped assets
        # WHY: Show current state
        # HOW: Query and map pk to 'id' for consistency with frontend
        dropped_qs = AcqAsset.objects.filter(
            trade=self.trade,
            acq_status=AcqAsset.AcquisitionStatus.DROP
        ).select_related('loan', 'property').values(
            'pk',
            'loan__sellertape_id',
            'property__street_address',
            'property__city',
            'property__state',
            'loan__current_balance',
            'updated_at'
        )
        
        # WHAT: Map 'pk' key to 'id' for consistency with other return dictionaries
        # WHY: Frontend expects 'id' key, and asset_hub is the primary key (no separate id field)
        # HOW: List comprehension to create new dicts with renamed key
        dropped = [
            {
                'id': asset.get('pk'),
                'sellertape_id': asset.get('loan__sellertape_id'),
                'street_address': asset.get('property__street_address') or '',
                'city': asset.get('property__city') or '',
                'state': asset.get('property__state') or '',
                'current_balance': asset.get('loan__current_balance') or 0,
                'updated_at': asset.get('updated_at'),
            }
            for asset in dropped_qs
        ]
        
        # WHAT: Get count of kept assets
        # WHY: Show summary
        kept_count = AcqAsset.objects.filter(
            trade=self.trade,
            acq_status=AcqAsset.AcquisitionStatus.KEEP
        ).count()
        
        return {
            'dropped_assets': dropped,
            'dropped_count': len(dropped),
            'kept_count': kept_count,
            'trade_name': self.trade.trade_name
        }
