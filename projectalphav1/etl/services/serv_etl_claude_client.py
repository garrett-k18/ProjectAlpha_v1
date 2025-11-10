"""Claude API helper for valuation extraction.

Provides a small callable that matches the ClaudeFieldAugmenter client contract.
The callable returns a dictionary with ``value``/``confidence`` keys parsed from
Claude's JSON response, or an empty dict if the call fails.
"""

from __future__ import annotations

import base64
import json
import logging
import os
from typing import Any, Callable, Dict, Iterable, Optional

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import anthropic
except Exception:  # pragma: no cover - best effort optional import
    anthropic = None  # type: ignore


def build_valuation_claude_client(
    *,
    default_model: str = "claude-3-haiku-20240307",
    max_tokens: int = 400,
) -> Optional[Callable[[str, Dict[str, Any]], Dict[str, Any]]]:
    """Return a callable suitable for ClaudeFieldAugmenter."""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY is not set; Claude fallback will be disabled.")
        return None

    if anthropic is None:
        logger.warning("anthropic package is unavailable; Claude fallback will be disabled.")
        return None

    client = anthropic.Anthropic(api_key=api_key)

    def _call_claude(prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        model = context.get("model") or default_model
        field_name = context.get("field", "unknown")
        try:
            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0,
                system="You are extracting structured data from valuation documents.",
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:  # pragma: no cover - network failures
            logger.warning("Claude API call failed for %s: %s", field_name, exc)
            return {}

        response_text = ""
        for block in getattr(message, "content", []):
            if isinstance(block, dict):
                response_text += str(block.get("text", ""))
            else:
                response_text += getattr(block, "text", "")

        payload = _parse_claude_payload(response_text, field_name)
        if not payload:
            return {}

        value = payload.get("value")
        if value in (None, ""):
            return {}

        payload.setdefault("confidence", 0.6)
        return payload

    return _call_claude


def build_valuation_claude_vision_client(
    *,
    default_model: str = "claude-3-5-haiku-20241022",
    max_tokens: int = 4096,
) -> Optional[Callable[[bytes], Dict[str, Any]]]:
    """Return a callable that posts full documents to Claude Vision."""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY is not set; Claude vision extraction will be disabled.")
        return None

    if anthropic is None:
        logger.warning("anthropic package is unavailable; Claude vision extraction will be disabled.")
        return None

    client = anthropic.Anthropic(api_key=api_key)

    def _call_vision(*, file_bytes: bytes, mime_type: str, prompt: str) -> Dict[str, Any]:
        encoded = base64.b64encode(file_bytes).decode("ascii")
        content_type = "document" if mime_type == "application/pdf" else "image"

        try:
            message = client.messages.create(
                model=default_model,
                max_tokens=max_tokens,
                temperature=0,
                system=(
                    "You are extracting structured data from valuation documents. "
                    "Return ONLY valid JSON with the requested structure."
                ),
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": content_type,
                                "source": {
                                    "type": "base64",
                                    "media_type": mime_type,
                                    "data": encoded,
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )
        except Exception as exc:  # pragma: no cover - network failures
            logger.warning("Claude vision API call failed: %s", exc)
            return {}

        response_text = ""
        for block in getattr(message, "content", []):
            if isinstance(block, dict):
                response_text += str(block.get("text", ""))
            else:
                response_text += getattr(block, "text", "")

        payload = _parse_claude_payload(response_text, "vision_response")
        if not payload:
            return {}
        return payload

    return _call_vision


def _parse_claude_payload(response_text: str, field_name: str) -> Optional[Dict[str, Any]]:
    response_text = (response_text or "").strip()
    if not response_text:
        return None

    if response_text.startswith("```"):
        parts = response_text.split("\n")
        response_text = "\n".join(parts[1:-1])

    candidates = list(_extract_json_segments(response_text)) or [response_text]

    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and payload:
            return payload

    logger.warning(
        "Claude returned non-JSON response for %s: %s",
        field_name,
        response_text[:200],
    )
    return None


def _extract_json_segments(text: str) -> Iterable[str]:
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
