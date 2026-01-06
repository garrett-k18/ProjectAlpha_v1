"""
Service for generating and managing AI-powered note summaries.

WHAT: Provides functions to generate structured AI summaries of notes for asset hubs.
WHY: Centralizes summary generation logic with consistent prompts and caching.
HOW: Uses Google Gemini API with structured prompts to generate consistent summaries.

Docs reviewed:
- Google Generative AI Python SDK: https://ai.google.dev/gemini-api/docs/quickstart?lang=python
- Django signals: https://docs.djangoproject.com/en/stable/topics/signals/
"""

from typing import Dict, List, Optional
import os
import logging
import hashlib
import json

from django.utils import timezone
from django.db import transaction

from am_module.models.model_am_amData import AMNote, AMNoteSummary
from core.models.model_co_assetIdHub import AssetIdHub

# Attempt to import Google Generative AI SDK
try:
    import google.generativeai as genai
    _GEMINI_AVAILABLE = True
except Exception:
    _GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

# WHAT: Configuration constants for AI summary generation
# WHY: Allows easy tuning of model, output size, and behavior
# HOW: Can be overridden via environment variables
_MODEL_NAME = os.getenv("AI_SUMMARY_MODEL", "gemini-2.5-flash")  # Gemini Flash 2.5 - cost-effective option
_MAX_OUTPUT_TOKENS = int(os.getenv("AI_SUMMARY_MAX_TOKENS", "2048"))  # Gemini supports higher token limits
_TEMPERATURE = float(os.getenv("AI_SUMMARY_TEMPERATURE", "0.3"))  # Slightly higher for more natural summaries


def _compute_notes_hash(notes: List[AMNote]) -> str:
    """
    WHAT: Computes a hash of note IDs and updated_at timestamps.
    WHY: Detects when notes have changed so we know when to regenerate summary.
    HOW: Creates a deterministic hash from note IDs and timestamps.
    
    Args:
        notes: List of AMNote objects to hash
        
    Returns:
        SHA256 hash string of note IDs and timestamps
    """
    # WHAT: Sort notes by ID for consistent hashing
    # WHY: Ensures same set of notes always produces same hash
    # HOW: Sort by ID, then create string representation
    sorted_notes = sorted(notes, key=lambda n: n.id)
    
    # WHAT: Create string representation of note IDs and timestamps
    # WHY: Need consistent string format for hashing
    # HOW: Join note ID and updated_at timestamp for each note
    hash_input = "|".join([
        f"{note.id}:{note.updated_at.isoformat()}" 
        for note in sorted_notes
    ])
    
    # WHAT: Compute SHA256 hash
    # WHY: SHA256 provides good collision resistance
    # HOW: Use hashlib to create hash, return hex digest
    return hashlib.sha256(hash_input.encode()).hexdigest()


def _build_structured_prompt(notes: List[AMNote]) -> str:
    """
    WHAT: Builds a structured prompt for consistent AI summary generation.
    WHY: Structured prompts produce more consistent and useful summaries.
    HOW: Formats notes data with clear instructions and context.
    
    Args:
        notes: List of AMNote objects to summarize
        
    Returns:
        Formatted prompt string for AI model
    """
    # WHAT: Extract and format note data for prompt
    # WHY: Need clean, structured data for AI to process
    # HOW: Build list of formatted note strings
    note_entries = []
    for i, note in enumerate(notes, 1):
        # WHAT: Strip HTML tags from note body for cleaner text
        # WHY: HTML adds noise that doesn't help AI understanding
        # HOW: Simple regex replacement (basic, but sufficient for our use case)
        import re
        body_text = re.sub(r'<[^>]+>', '', note.body or '').strip()
        
        # WHAT: Build formatted note entry
        # WHY: Structured format helps AI understand context
        # HOW: Include note number, tag, date, author, and content
        tag_str = f" [{note.tag.upper()}]" if note.tag else ""
        author_str = f" by {note.created_by.username}" if note.created_by else ""
        date_str = note.created_at.strftime("%Y-%m-%d")
        
        note_entry = (
            f"Note {i}{tag_str} - {date_str}{author_str}:\n"
            f"{body_text}\n"
        )
        note_entries.append(note_entry)
    
    # WHAT: Combine all note entries into single text block
    # WHY: AI needs all context in one place
    # HOW: Join entries with separator
    notes_text = "\n---\n".join(note_entries)
    
    # WHAT: Build structured prompt with clear instructions
    # WHY: Clear instructions produce more consistent results
    # HOW: Use multi-line string with specific format requirements
    prompt = f"""Analyze the following notes for an asset and provide a comprehensive summary.

INSTRUCTIONS:
1. Provide a 2-3 sentence executive summary that captures the most important themes and current status.
2. List 4-6 key bullet points focusing on:
   - Critical issues or risks that need attention
   - Important decisions or actions taken
   - Recent developments or changes
   - Key stakeholders or contacts mentioned
   - Any urgent or legal matters
3. Prioritize information that is actionable or requires follow-up.
4. Be concise but informative - bullets dont need to be full complete sentences but try to keep one sentence, but max 2 sentences.
5. Do not use borrower or heir names, or other PII in the summary or bullets.
6. Do NOT use markdown formatting (no **, no *, no bold/italic markers). Write plain text only.
7. For bullet points, use the format: "Label: Description" where Label is a short phrase (2-4 words) followed by a colon, then the description.

OUTPUT FORMAT:
Return your response in this exact format:

EXECUTIVE_SUMMARY:
[2-3 sentence summary here]

KEY_POINTS:
- [First key point]
- [Second key point]
- [Third key point]
- [Fourth key point]
- [Fifth key point]
- [Sixth key point (if applicable)]

NOTES TO ANALYZE:
{notes_text}

Now provide the summary following the format above:"""
    
    return prompt


def _parse_ai_response(response_text: str) -> Dict[str, any]:
    """
    WHAT: Parses AI response into structured summary data.
    WHY: AI responses need to be extracted into consistent format.
    HOW: Searches for EXECUTIVE_SUMMARY and KEY_POINTS sections.
    
    Args:
        response_text: Raw text response from AI model
        
    Returns:
        Dictionary with 'summary_text' and 'bullets' keys
    """
    # WHAT: Initialize default values
    # WHY: Need fallbacks if parsing fails
    # HOW: Set empty strings/lists as defaults
    summary_text = ""
    bullets = []
    
    # WHAT: Extract executive summary section
    # WHY: Need to find and extract the summary text
    # HOW: Search for EXECUTIVE_SUMMARY marker
    summary_start = response_text.find("EXECUTIVE_SUMMARY:")
    summary_end = response_text.find("KEY_POINTS:")
    
    if summary_start != -1:
        # WHAT: Extract text between markers
        # WHY: Get the actual summary content
        # HOW: Slice string between markers, clean up whitespace
        if summary_end != -1:
            summary_text = response_text[summary_start + len("EXECUTIVE_SUMMARY:"):summary_end].strip()
        else:
            summary_text = response_text[summary_start + len("EXECUTIVE_SUMMARY:"):].strip()
        # WHAT: Remove leading colon and whitespace if present
        # WHY: Clean up formatting artifacts
        # HOW: Strip and replace newlines with spaces
        summary_text = summary_text.replace("\n", " ").strip()
    
    # WHAT: Extract key points section
    # WHY: Need to get bullet points
    # HOW: Search for KEY_POINTS marker and parse bullet lines
    points_start = response_text.find("KEY_POINTS:")
    if points_start != -1:
        # WHAT: Get text after KEY_POINTS marker
        # WHY: Contains the bullet points
        # HOW: Slice from marker to end (or next section if exists)
        points_text = response_text[points_start + len("KEY_POINTS:"):].strip()
        
        # WHAT: Split into lines and extract bullets
        # WHY: Each bullet is on its own line
        # HOW: Iterate through lines, look for bullet markers
        for line in points_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            # WHAT: Check for bullet markers (-, •, *)
            # WHY: AI may use different bullet styles
            # HOW: Remove marker and add to bullets list
            if line.startswith("- "):
                bullets.append(line[2:].strip())
            elif line.startswith("• "):
                bullets.append(line[2:].strip())
            elif line.startswith("* "):
                bullets.append(line[2:].strip())
            elif line and len(bullets) < 6:  # WHAT: Accept lines without markers if we need more bullets
                bullets.append(line)
    
    # WHAT: Fallback if parsing failed
    # WHY: Ensure we always return something
    # HOW: Use first paragraph as summary, split response into bullets
    if not summary_text and not bullets:
        lines = [l.strip() for l in response_text.split("\n") if l.strip()]
        if lines:
            summary_text = lines[0]
            bullets = lines[1:7]  # Take up to 6 more lines as bullets
    
    # WHAT: Ensure we have at least some content
    # WHY: Frontend expects non-empty data
    # HOW: Add default message if empty
    if not summary_text:
        summary_text = "Summary of asset notes and activities."
    if not bullets:
        bullets = ["No key points extracted from notes."]
    
    # WHAT: Limit bullets to 6 maximum
    # WHY: Keep summary concise
    # HOW: Slice to first 6 items
    bullets = bullets[:6]
    
    return {
        "summary_text": summary_text,
        "bullets": bullets,
    }


@transaction.atomic
def generate_note_summary(asset_hub_id: int, force_regenerate: bool = False) -> Optional[AMNoteSummary]:
    """
    WHAT: Generates or retrieves cached AI summary for an asset hub's notes.
    WHY: Provides efficient summary generation with caching and change detection.
    HOW: Checks if summary exists and is current, regenerates only if needed.
    
    Args:
        asset_hub_id: ID of the AssetIdHub to generate summary for
        force_regenerate: If True, regenerate even if summary exists and is current
        
    Returns:
        AMNoteSummary object or None if generation failed
    """
    # WHAT: Get asset hub object
    # WHY: Need to verify asset exists and access notes
    # HOW: Use get_object_or_404 equivalent (we'll handle None)
    try:
        asset_hub = AssetIdHub.objects.get(pk=asset_hub_id)
    except AssetIdHub.DoesNotExist:
        logger.error(f"Asset hub {asset_hub_id} not found for summary generation")
        return None
    
    # WHAT: Fetch all notes for this asset hub
    # WHY: Need all notes to generate comprehensive summary
    # HOW: Query AMNote model filtered by asset_hub
    notes = list(AMNote.objects.filter(asset_hub_id=asset_hub_id).order_by("-created_at"))
    
    # WHAT: Log note count for debugging
    # WHY: Help diagnose why summary might not be generated
    # HOW: Log the count of notes found
    logger.debug(f"Found {len(notes)} notes for asset hub {asset_hub_id}")
    
    # WHAT: Handle case where no notes exist
    # WHY: Can't generate summary without notes
    # HOW: Return None or create empty summary
    if not notes:
        # WHAT: Delete existing summary if it exists (no notes = no summary)
        # WHY: Keep data consistent
        # HOW: Delete if exists
        logger.debug(f"No notes found for asset hub {asset_hub_id}, deleting any existing summary")
        AMNoteSummary.objects.filter(asset_hub_id=asset_hub_id).delete()
        return None
    
    # WHAT: Compute hash of current notes
    # WHY: Detect if notes have changed since last summary
    # HOW: Use _compute_notes_hash function
    current_hash = _compute_notes_hash(notes)
    
    # WHAT: Check if summary already exists and is current
    # WHY: Avoid unnecessary API calls and improve performance
    # HOW: Query AMNoteSummary and compare hashes
    try:
        existing_summary = AMNoteSummary.objects.get(asset_hub_id=asset_hub_id)
        
        # WHAT: Check if summary is still valid (hash matches)
        # WHY: Only regenerate if notes have changed
        # HOW: Compare stored hash with current hash
        if not force_regenerate and existing_summary.notes_hash == current_hash:
            # WHAT: Summary is still valid, return it
            # WHY: No need to regenerate
            # HOW: Return existing summary object
            return existing_summary
        
        # WHAT: Notes have changed, need to regenerate
        # WHY: Summary is out of date
        # HOW: Continue to generation logic below
    except AMNoteSummary.DoesNotExist:
        # WHAT: No summary exists yet, need to create one
        # WHY: First time generating summary for this asset
        # HOW: Continue to generation logic below
        existing_summary = None
    
    # WHAT: Check if Gemini SDK is available
    # WHY: Can't generate summary without API access
    # HOW: Check _GEMINI_AVAILABLE flag
    if not _GEMINI_AVAILABLE:
        error_msg = f"Google Generative AI SDK not available for summary generation (asset hub {asset_hub_id}). Notes exist ({len(notes)} notes) but cannot generate summary - SDK unavailable. Please install google-generativeai package."
        logger.error(error_msg)
        if existing_summary:
            return existing_summary  # Return existing if available
        raise Exception(error_msg)
    
    # WHAT: Get API key from environment (check both GEMINI_API_KEY and GOOGLE_API_KEY)
    # WHY: Gemini API key can be set as either variable name
    # HOW: Read from os.getenv, prefer GOOGLE_API_KEY if both exist
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        error_msg = f"GEMINI_API_KEY or GOOGLE_API_KEY not set in environment (asset hub {asset_hub_id}). Notes exist ({len(notes)} notes) but cannot generate summary - API key missing."
        logger.error(error_msg)
        if existing_summary:
            return existing_summary  # Return existing if available
        raise Exception(error_msg)
    
    # WHAT: Build structured prompt from notes
    # WHY: Need formatted prompt for consistent AI responses
    # HOW: Use _build_structured_prompt function
    prompt = _build_structured_prompt(notes)
    
    try:
        # WHAT: Configure Gemini API client
        # WHY: Need to set API key before making requests
        # HOW: Use genai.configure with API key
        genai.configure(api_key=api_key)
        logger.debug(f"Configured Gemini API with model: {_MODEL_NAME}")
        
        # WHAT: Create GenerativeModel instance with specified model
        # WHY: Gemini uses model instances for generation
        # HOW: Use genai.GenerativeModel with model_name (not model) and generation config
        try:
            model = genai.GenerativeModel(
                model_name=_MODEL_NAME,  # WHAT: Use model_name, not model (correct parameter name)
                generation_config={
                    "temperature": _TEMPERATURE,
                    "max_output_tokens": _MAX_OUTPUT_TOKENS,
                }
            )
            logger.debug(f"Created GenerativeModel instance for {_MODEL_NAME}")
        except Exception as model_error:
            logger.error(f"Failed to create GenerativeModel: {model_error}")
            # WHAT: Try with a fallback model name
            # WHY: Model name might be incorrect or unavailable
            # HOW: Try gemini-2.0-flash-exp or gemini-1.5-flash
            fallback_models = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-pro"]
            model = None
            for fallback_model in fallback_models:
                try:
                    logger.info(f"Trying fallback model: {fallback_model}")
                    model = genai.GenerativeModel(
                        model_name=fallback_model,  # WHAT: Use model_name, not model
                        generation_config={
                            "temperature": _TEMPERATURE,
                            "max_output_tokens": _MAX_OUTPUT_TOKENS,
                        }
                    )
                    logger.info(f"Successfully created model with fallback: {fallback_model}")
                    break
                except Exception as fallback_error:
                    logger.debug(f"Fallback model {fallback_model} failed: {fallback_error}")
                    continue
            if model is None:
                raise Exception(f"Could not create GenerativeModel with {_MODEL_NAME} or any fallback models. Original error: {model_error}")
        
        # WHAT: Call Gemini API to generate summary
        # WHY: AI generates better summaries than simple text extraction
        # HOW: Use generate_content method with prompt
        logger.debug(f"Calling Gemini API to generate summary for {len(notes)} notes")
        response = model.generate_content(prompt)
        logger.debug(f"Received response from Gemini API")
        
        # WHAT: Check for blocked responses or safety filters
        # WHY: Gemini may block content based on safety settings
        # HOW: Check prompt_feedback and candidates for blocks
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
            if hasattr(response.prompt_feedback, 'block_reason'):
                logger.warning(f"Gemini blocked response for asset hub {asset_hub_id}: {response.prompt_feedback.block_reason}")
                raise Exception(f"Content blocked by safety filters: {response.prompt_feedback.block_reason}")
        
        # WHAT: Check if response was blocked in candidates
        # WHY: Candidates may be blocked even if prompt_feedback doesn't show it
        # HOW: Check finish_reason in candidates
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                if candidate.finish_reason not in ['STOP', None]:
                    logger.warning(f"Gemini response finished with reason: {candidate.finish_reason} for asset hub {asset_hub_id}")
                    if candidate.finish_reason in ['SAFETY', 'RECITATION']:
                        raise Exception(f"Response blocked: {candidate.finish_reason}")
        
        # WHAT: Extract text from API response
        # WHY: Gemini returns response object with text attribute or parts
        # HOW: Access response.text or iterate through response.parts
        full_text = ""
        try:
            # WHAT: Try direct text access first (most common)
            # WHY: Most responses have text attribute
            # HOW: Access text attribute directly
            if hasattr(response, 'text') and response.text:
                full_text = str(response.text).strip()
        except Exception as e:
            logger.debug(f"Could not access response.text: {e}")
        
        # WHAT: Fallback to parts if text not available
        # WHY: Some responses may use parts structure
        # HOW: Extract text from each part
        if not full_text and hasattr(response, 'parts') and response.parts:
            text_parts = []
            for part in response.parts:
                try:
                    if hasattr(part, 'text') and part.text:
                        text_parts.append(str(part.text))
                except Exception:
                    pass
            if text_parts:
                full_text = "\n".join(text_parts).strip()
        
        # WHAT: Fallback to candidates structure
        # WHY: Some API versions use candidates
        # HOW: Extract text from first candidate's content
        if not full_text and hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                text_parts = []
                for part in candidate.content.parts:
                    try:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(str(part.text))
                    except Exception:
                        pass
                if text_parts:
                    full_text = "\n".join(text_parts).strip()
        
        # WHAT: Log warning if no text extracted
        # WHY: Help debug API response issues
        # HOW: Log response structure if empty
        if not full_text:
            logger.error(f"Gemini API returned empty response for asset hub {asset_hub_id}")
            logger.error(f"Response type: {type(response)}")
            if hasattr(response, '__dict__'):
                logger.error(f"Response attributes: {list(response.__dict__.keys())}")
            if hasattr(response, 'candidates') and response.candidates:
                logger.error(f"First candidate finish_reason: {getattr(response.candidates[0], 'finish_reason', 'N/A')}")
            raise Exception("Gemini API returned empty response - check logs for details")
        
        # WHAT: Parse AI response into structured data
        # WHY: Need consistent format for storage
        # HOW: Use _parse_ai_response function
        summary_data = _parse_ai_response(full_text)
        
        # WHAT: Add metadata to summary data
        # WHY: Track generation details
        # HOW: Add timestamp and note count
        summary_data["generated_at"] = timezone.now().isoformat()
        summary_data["note_count"] = len(notes)
        
        # WHAT: Save or update summary record
        # WHY: Persist summary for future use
        # HOW: Use get_or_create, then update fields
        if existing_summary:
            # WHAT: Update existing summary
            # WHY: Notes changed, need new summary
            # HOW: Update fields on existing object
            existing_summary.summary_data = summary_data
            existing_summary.notes_hash = current_hash
            existing_summary.generated_at = timezone.now()
            existing_summary.save()
            return existing_summary
        else:
            # WHAT: Create new summary record
            # WHY: First time generating summary for this asset
            # HOW: Create new AMNoteSummary object
            new_summary = AMNoteSummary.objects.create(
                asset_hub=asset_hub,
                summary_data=summary_data,
                notes_hash=current_hash,
                generated_at=timezone.now(),
            )
            return new_summary
            
    except Exception as e:
        # WHAT: Log error and return existing summary if available
        # WHY: Don't break UI if generation fails
        # HOW: Log exception with full details for debugging
        logger.exception(f"Failed to generate note summary for asset hub {asset_hub_id}")
        logger.error(f"Error type: {type(e).__name__}, Error message: {str(e)}")
        
        # WHAT: Check if it's a Gemini API specific error
        # WHY: Different error types need different handling
        # HOW: Check error attributes
        error_details = []
        if hasattr(e, 'message'):
            error_details.append(f"message: {e.message}")
        if hasattr(e, 'prompt_feedback'):
            error_details.append(f"prompt_feedback: {e.prompt_feedback}")
        if hasattr(e, 'args') and e.args:
            error_details.append(f"args: {e.args}")
        if hasattr(e, '__dict__'):
            error_details.append(f"attributes: {list(e.__dict__.keys())}")
        
        if error_details:
            logger.error(f"Gemini API error details: {'; '.join(error_details)}")
        
        # WHAT: Re-raise exception with more context
        # WHY: View needs to know what went wrong
        # HOW: Raise new exception with helpful message
        raise Exception(f"Gemini summary generation failed: {str(e)}") from e

