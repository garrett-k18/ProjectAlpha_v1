"""
Server-side AI summary endpoint using Anthropic.

Docs reviewed:
- Anthropic Python SDK: https://docs.anthropic.com/en/api/messages
- DRF function views: https://www.django-rest-framework.org/api-guide/views/#function-based-views
- Django CSRF notes (API endpoints): https://docs.djangoproject.com/en/5.2/ref/csrf/

This endpoint keeps the API key on the server and returns 4–6 concise bullet points.
"""
from typing import List, Tuple, Dict
import os
import logging
import time

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Attempt to import Anthropics' SDK. If unavailable, return a helpful error.
try:  # Try to import the official SDK (preferred)
    import anthropic  # type: ignore
    _ANTHROPIC_AVAILABLE = True
except Exception:
    _ANTHROPIC_AVAILABLE = False


def _extract_bullets_from_text(text: str, limit: int) -> List[str]:
    """Best-effort extraction of bullet lines from a text block.
    - Accepts lines starting with '- ', '• ', or '* '.
    - Trims markers and whitespace.
    - Returns up to `limit` items.
    """
    bullets: List[str] = []
    for raw in (text or '').splitlines():
        line = (raw or '').strip()
        if not line:
            continue
        if line.startswith(('- ', '• ', '* ')):
            line = line[2:].strip()
        bullets.append(line)
        if len(bullets) >= limit:
            break
    return bullets


# --------------------------------------------------------------------------------------
# Low-latency defaults and lightweight cache
# Docs reviewed:
# - Anthropic models: https://docs.anthropic.com/en/docs/about-claude/models
#   (Haiku prioritized for latency; Sonnet for higher quality)
# --------------------------------------------------------------------------------------
# Allow overriding via environment for flexibility across environments
_MODEL_NAME = os.getenv("AI_SUMMARY_MODEL", "claude-3-haiku-20240307")
# Output tokens needed for 4–6 short bullets; keep conservative to reduce latency
_MAX_OUTPUT_TOKENS = int(os.getenv("AI_SUMMARY_MAX_TOKENS", "150"))
# Lower temperature to minimize dithering and slightly speed decoding
_TEMPERATURE = float(os.getenv("AI_SUMMARY_TEMPERATURE", "0"))

# Simple in-memory cache (per-process). Suitable for dev and single-process deployments.
# Key: (context_hash, max_bullets, model)
_CACHE_TTL = int(os.getenv("AI_SUMMARY_CACHE_TTL", "600"))  # seconds
_CACHE_MAX_ENTRIES = int(os.getenv("AI_SUMMARY_CACHE_MAX", "200"))
_cache: Dict[Tuple[int, int, str], Tuple[float, List[str]]] = {}

def _cache_get(key: Tuple[int, int, str]) -> List[str] | None:
    now = time.time()
    item = _cache.get(key)
    if not item:
        return None
    ts, value = item
    if now - ts > _CACHE_TTL:
        # expired
        try:
            del _cache[key]
        except Exception:
            pass
        return None
    return value

def _cache_set(key: Tuple[int, int, str], value: List[str]) -> None:
    # Trim cache if it grows too large
    if len(_cache) >= _CACHE_MAX_ENTRIES:
        try:
            # Remove oldest item (approximate by timestamp scan)
            oldest_key = min(_cache.items(), key=lambda kv: kv[1][0])[0]
            del _cache[oldest_key]
        except Exception:
            _cache.clear()
    _cache[key] = (time.time(), value)


@csrf_exempt  # Using token auth or anonymous in dev; CSRF exempt simplifies local testing
@api_view(["POST"])  # Function-based DRF view for simplicity and clarity
@permission_classes([AllowAny])  # Adjust in production as needed
def generate_quick_summary(request):
    """Generate 4–6 bullet points summarizing the posted context.

    Request JSON:
    - context: str (required)  -> the raw content to summarize
    - max_bullets: int (opt)   -> desired bullet count (clamped to [4,6])

    Response JSON:
    - { bullets: string[] }
    - or { bullets: [], error: string }
    """
    data = request.data or {}
    context: str = (data.get("context") or "").strip()
    try:
        max_bullets = int(data.get("max_bullets", 5))
    except Exception:
        max_bullets = 5
    # Clamp to 4..6 to match UX expectations
    max_bullets = max(4, min(6, max_bullets))

    if len(context) < 10:  # Require some substance
        return Response({"bullets": [], "error": "insufficient_context"}, status=400)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return Response({"bullets": [], "error": "missing_api_key"}, status=500)

    if not _ANTHROPIC_AVAILABLE:
        return Response({"bullets": [], "error": "anthropic_sdk_missing"}, status=500)

    # Build a precise prompt to return only bullet lines for robust parsing
    user_prompt = (
        f"Summarize the following content into {max_bullets} concise bullet points.\n"
        "Focus on key facts, risks, and actionable insights.\n"
        "Return ONLY the bullet points lines, each starting with '- '. No intro, no outro.\n\n"
        "CONTENT:\n"
        f"{context}"
    )

    try:
        # Check cache first (hashing context to keep key size modest)
        ctx_hash = hash(context)
        cache_key = (ctx_hash, max_bullets, _MODEL_NAME)
        cached = _cache_get(cache_key)
        if cached is not None:
            return Response({"bullets": cached})

        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=_MODEL_NAME,  # Default fast model; override via AI_SUMMARY_MODEL
            max_tokens=_MAX_OUTPUT_TOKENS,
            temperature=_TEMPERATURE,
            messages=[{"role": "user", "content": user_prompt}],
        )

        # Anthropic Messages API returns a list of content blocks.
        # Collect text from all blocks to be safe across SDK versions.
        text_parts: List[str] = []
        content = getattr(msg, "content", None)
        if content and isinstance(content, list):
            for block in content:
                # Blocks often have .text or {"type":"text","text":"..."}
                block_text = getattr(block, "text", None)
                if block_text is None and isinstance(block, dict):
                    block_text = block.get("text")
                if block_text:
                    text_parts.append(str(block_text))
        full_text = "\n".join(text_parts).strip()

        bullets = _extract_bullets_from_text(full_text, limit=max_bullets)
        # Fallback if model ignored instructions
        if not bullets and full_text:
            bullets = _extract_bullets_from_text("- " + full_text.replace("\n", "\n- "), limit=max_bullets)
        if not bullets:
            bullets = ["No key points extracted."]

        # Save to cache for subsequent identical requests
        _cache_set(cache_key, bullets)

        return Response({"bullets": bullets})

    except Exception:
        logging.exception("[AI] Anthropic summary generation failed")
        return Response({"bullets": [], "error": "provider_error"}, status=502)
