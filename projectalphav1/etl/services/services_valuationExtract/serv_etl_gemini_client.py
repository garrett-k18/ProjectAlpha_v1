"""Gemini API helper for valuation extraction.

Provides a callable that interfaces with Google's Gemini 2.5 Flash model for
document vision processing. The callable returns a dictionary with extracted
fields parsed from Gemini's JSON response, or an empty dict if the call fails.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import time
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

# Import google-generativeai library (optional dependency)
try:  # pragma: no cover - optional dependency
    import google.generativeai as genai
except Exception:  # pragma: no cover - best effort optional import
    genai = None  # type: ignore


# WHAT: Shared Gemini Vision client builder for ETL extractors.
# WHY: Reused by valuation and trade settlement extraction workflows.
def build_valuation_gemini_vision_client(
    *,
    default_model: str = "gemini-2.5-flash",
    max_output_tokens: int = 8192,  # Gemini default, can go higher if needed
) -> Optional[Callable[[bytes], Dict[str, Any]]]:
    """Return a callable that posts full documents to Gemini Vision API.
    
    Args:
        default_model: The Gemini model to use (default: gemini-2.5-flash)
        max_output_tokens: Maximum tokens in the response (default: 8192, Gemini can handle much more)
    
    Returns:
        A callable that accepts file_bytes, mime_type, and prompt and returns extracted data
    """
    
    # Get the API key from environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set; Gemini vision extraction will be disabled.")
        return None

    # Check if google-generativeai is available
    if genai is None:
        logger.warning("google-generativeai package is unavailable; Gemini vision extraction will be disabled.")
        return None

    # Configure the Gemini API with the API key
    genai.configure(api_key=api_key)

    def _call_vision(*, file_bytes: bytes, mime_type: str, prompt: str) -> Dict[str, Any]:
        """Call Gemini Vision API to extract data from document.
        
        Args:
            file_bytes: The document bytes to process
            mime_type: The MIME type of the document (e.g., 'application/pdf')
            prompt: The extraction prompt to send to the model
        
        Returns:
            Dictionary containing extracted data or empty dict on failure
        """
        import tempfile
        import os
        
        temp_file_path = None
        try:
            # Log the request details
            logger.info("=" * 80)
            logger.info("STEP 1: Starting Gemini vision extraction")
            logger.info("  File size: %d bytes (%.2f MB)", len(file_bytes), len(file_bytes) / 1024 / 1024)
            logger.info("  MIME type: %s", mime_type)
            logger.info("  Model: %s", default_model)
            logger.info("=" * 80)
            
            # Create a temporary file for upload
            # Gemini's upload_file API requires a file path
            file_extension = ".pdf" if mime_type == "application/pdf" else ".jpg"
            logger.info("STEP 2: Creating temporary file...")
            temp_fd, temp_file_path = tempfile.mkstemp(suffix=file_extension, prefix="gemini_upload_")
            
            try:
                # Write the bytes to the temporary file
                with os.fdopen(temp_fd, 'wb') as temp_file:
                    temp_file.write(file_bytes)
                
                # Upload the file to Gemini's file API
                # This allows processing of larger documents
                logger.info("STEP 3: Uploading to Gemini File API...")
                logger.info("  Temp file: %s", temp_file_path)
                logger.info("  MIME type: %s", mime_type)
                
                import time
                upload_start = time.time()
                
                uploaded_file = genai.upload_file(
                    path=temp_file_path,
                    mime_type=mime_type,
                )
                
                upload_time = time.time() - upload_start
                
                # Wait for the file to be processed
                # PDFs need time to be processed for vision/OCR
                logger.info("STEP 3 COMPLETE: Upload finished in %.1f seconds", upload_time)
                logger.info("  File ID: %s", uploaded_file.name)
                logger.info("  MIME type: %s", uploaded_file.mime_type)
                logger.info("  State: %s", uploaded_file.state.name if hasattr(uploaded_file, 'state') else 'unknown')
                
                # Wait for file to be in ACTIVE state (may need processing for PDFs)
                if hasattr(uploaded_file, 'state') and uploaded_file.state.name == 'PROCESSING':
                    logger.info("STEP 3b: Waiting for file processing...")
                    max_wait = 60  # seconds
                    wait_interval = 2  # seconds
                    elapsed = 0
                    
                    while uploaded_file.state.name == 'PROCESSING':
                        if elapsed >= max_wait:
                            logger.warning("  File still processing after %ds, proceeding anyway...", max_wait)
                            break
                        logger.info("  Waiting... (%ds elapsed)", elapsed)
                        time.sleep(wait_interval)
                        elapsed += wait_interval
                        # Re-fetch file status
                        uploaded_file = genai.get_file(uploaded_file.name)
                    
                    logger.info("  File processing complete. State: %s", uploaded_file.state.name)
                
            finally:
                # Clean up the local temporary file
                if temp_file_path and os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                    except Exception:
                        pass
            
            # Create the model instance with generation config
            # Let Gemini use its full output capacity
            model = genai.GenerativeModel(
                model_name=default_model,
                generation_config={
                    "temperature": 0.0,  # Deterministic output for data extraction
                    "top_p": 0.95,
                    "top_k": 40,
                    # No max_output_tokens limit - let Gemini decide based on model capacity
                }
            )
            
            # Create the content with both the document and the prompt
            # Gemini expects the file reference and text prompt together
            contents = [
                uploaded_file,
                prompt
            ]
            
            # Generate the response with timeout
            # Set request timeout to prevent hanging (max 120 seconds)
            logger.info("=" * 80)
            logger.info("STEP 4: Generating content from Gemini")
            logger.info("  Prompt length: %d characters", len(prompt))
            logger.info("  Estimated prompt tokens: ~%d", len(prompt) // 4)
            logger.info("  This may take 30-90 seconds...")
            logger.info("=" * 80)
            
            import time
            start_time = time.time()
            
            # Set a very high timeout (10 minutes) to allow for large extractions
            # The timeout is set in the request_options which is passed to the underlying gRPC client
            response = model.generate_content(
                contents,
                request_options={"timeout": 600.0}  # 10 minutes as float
            )
            
            elapsed = time.time() - start_time
            logger.info("=" * 80)
            logger.info("STEP 5: Gemini response received!")
            logger.info("  Generation time: %.1f seconds", elapsed)
            logger.info("=" * 80)
            
            # Clean up: delete the uploaded file from Gemini after processing
            try:
                genai.delete_file(uploaded_file.name)
                logger.info("Cleaned up uploaded file from Gemini: %s", uploaded_file.name)
            except Exception as cleanup_exc:
                logger.warning("Failed to delete uploaded file %s: %s", uploaded_file.name, cleanup_exc)
            
            # Extract the text from the response
            # Handle different response scenarios
            try:
                if not response:
                    logger.warning("Gemini returned None response")
                    return {}
                
                response_text = response.text.strip()
                
                if not response_text:
                    logger.warning("Gemini returned empty text")
                    logger.warning(f"Finish reason: {response.candidates[0].finish_reason if response.candidates else 'unknown'}")
                    return {}
                    
            except ValueError as e:
                # This happens when response.text fails (e.g., MAX_TOKENS)
                logger.error(f"Failed to get response text: {e}")
                if response.candidates:
                    finish_reason = response.candidates[0].finish_reason
                    logger.error(f"Finish reason: {finish_reason}")
                    if finish_reason == 2:  # MAX_TOKENS
                        logger.error("Response hit MAX_TOKENS limit. Increase max_output_tokens.")
                    elif finish_reason == 3:  # SAFETY
                        logger.error("Response blocked by safety filters.")
                return {}
            logger.info("=" * 80)
            logger.info("STEP 6: Processing response")
            logger.info("  Response length: %d characters (%.1f KB)", len(response_text), len(response_text) / 1024)
            logger.info("  First 200 chars: %s...", response_text[:200])
            logger.info("=" * 80)
            
            # Parse the JSON response
            logger.info("STEP 7: Parsing JSON...")
            parse_start = time.time()
            
            payload = _parse_gemini_payload(response_text, "vision_response")
            
            parse_time = time.time() - parse_start
            
            if not payload:
                logger.error("STEP 7 FAILED: Could not parse JSON")
                logger.error("  Raw text (first 1000 chars): %s", response_text[:1000])
                return {}
            
            logger.info("STEP 7 COMPLETE: JSON parsed in %.2f seconds", parse_time)
            logger.info("  Top-level keys: %s", list(payload.keys()))
            logger.info("  Key counts: valuation=%d fields, comparables=%d items, repairs=%d items",
                       len(payload.get('valuation', {})),
                       len(payload.get('comparables', [])),
                       len(payload.get('repairs', [])))
            
            # Debug: log sample of each key's content
            for key, value in payload.items():
                if isinstance(value, dict):
                    logger.debug(f"Key '{key}' is dict with {len(value)} items")
                    if value:
                        sample_keys = list(value.keys())[:5]
                        logger.debug(f"  Sample keys: {sample_keys}")
                elif isinstance(value, list):
                    logger.debug(f"Key '{key}' is list with {len(value)} items")
                else:
                    logger.debug(f"Key '{key}': {str(value)[:100]}")
            
            logger.info("=" * 80)
            logger.info("EXTRACTION COMPLETE - SUCCESS")
            logger.info("=" * 80)
            
            return payload
            
        except Exception as exc:  # pragma: no cover - network failures
            logger.error("Gemini vision API call failed: %s", exc, exc_info=True)
            # Clean up temp file on error
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
            return {}

    return _call_vision


def _call_vision_with_bytes(
    *,
    file_bytes: bytes,
    mime_type: str,
    prompt: str,
    model_name: str = "gemini-2.5-flash",
    max_output_tokens: int = 8192,
) -> Dict[str, Any]:
    """Direct call to Gemini Vision API using inline data (no file upload).
    
    This is a simpler approach for smaller files that can be sent directly
    without going through the File API.
    
    Args:
        file_bytes: The document bytes to process
        mime_type: The MIME type of the document
        prompt: The extraction prompt
        model_name: The Gemini model to use
        max_output_tokens: Maximum response tokens
    
    Returns:
        Dictionary containing extracted data or empty dict on failure
    """
    try:
        # Configure the model with generation settings
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.0,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": max_output_tokens,
                "response_mime_type": "application/json",
            }
        )
        
        # Create inline data content
        # Gemini can accept base64 encoded data directly for smaller files
        inline_data = {
            "mime_type": mime_type,
            "data": base64.b64encode(file_bytes).decode("utf-8")
        }
        
        # Generate content with inline data
        response = model.generate_content([
            {"inline_data": inline_data},
            prompt
        ])
        
        if not response or not response.text:
            logger.warning("Gemini returned empty response")
            return {}
        
        response_text = response.text.strip()
        payload = _parse_gemini_payload(response_text, "vision_response")
        
        return payload if payload else {}
        
    except Exception as exc:
        logger.error("Gemini inline vision call failed: %s", exc, exc_info=True)
        return {}


def _parse_gemini_payload(response_text: str, field_name: str) -> Optional[Dict[str, Any]]:
    """Parse Gemini's JSON response.
    
    Handles various JSON formats that Gemini might return, including:
    - Pure JSON
    - JSON wrapped in markdown code blocks
    - Multiple JSON objects (takes the first valid one)
    
    Args:
        response_text: The raw response text from Gemini
        field_name: Field name for logging purposes
    
    Returns:
        Parsed JSON dictionary or None if parsing fails
    """
    response_text = (response_text or "").strip()
    if not response_text:
        return None

    # Remove markdown code fences if present
    if response_text.startswith("```"):
        # Remove first line (```json or just ```)
        lines = response_text.split("\n")
        if len(lines) > 2:
            # Remove first and last lines
            response_text = "\n".join(lines[1:-1])
        else:
            response_text = response_text.replace("```", "")

    # Try to parse as JSON directly
    try:
        payload = json.loads(response_text)
        if isinstance(payload, dict) and payload:
            return payload
    except json.JSONDecodeError:
        pass

    # If direct parsing failed, try to extract JSON segments
    candidates = list(_extract_json_segments(response_text)) or [response_text]

    for candidate in candidates:
        try:
            payload = json.loads(candidate)
            if isinstance(payload, dict) and payload:
                return payload
        except json.JSONDecodeError:
            continue

    # Log warning if we couldn't parse the response
    logger.warning(
        "Gemini returned non-JSON response for %s: %s",
        field_name,
        response_text[:200],
    )
    return None


def _extract_json_segments(text: str):
    """Extract JSON objects from text by tracking brace depth.
    
    This function finds all complete JSON objects in a text string,
    even if there are multiple objects or surrounding text.
    
    Args:
        text: Text potentially containing JSON objects
    
    Yields:
        String segments that represent complete JSON objects
    """
    depth = 0
    start_index: Optional[int] = None
    
    for index, char in enumerate(text):
        if char == "{":
            if depth == 0:
                start_index = index
            depth += 1
        elif char == "}":
            if depth == 0:
                continue
            depth -= 1
            if depth == 0 and start_index is not None:
                yield text[start_index : index + 1]
                start_index = None


__all__ = [
    "build_valuation_gemini_vision_client",
]

