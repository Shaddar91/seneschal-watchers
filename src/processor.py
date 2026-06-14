import json
import logging
import httpx
from .config import settings

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """You are a regulatory change analyst. Given the following diff of a regulatory webpage, extract:
1. title: a short title describing what changed
2. summary: 1-3 sentence summary of the change
3. severity: one of "critical", "high", "medium", "low", "informational"

Respond ONLY with valid JSON: {"title": "...", "summary": "...", "severity": "..."}

DIFF:
{diff_text}"""


async def extract_change(diff_text: str) -> dict:
    """Send diff to AI model for extraction and classification."""
    prompt = EXTRACTION_PROMPT.format(diff_text=diff_text[:4000])

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{settings.ai_api_url}/api/generate",
            json={
                "model": settings.ai_model,
                "prompt": prompt,
                "stream": False,
            },
        )
        resp.raise_for_status()
        raw = resp.json().get("response", "")

    try:
        result = json.loads(raw)
        logger.info("extracted change", extra={"title": result.get("title")})
        return result
    except json.JSONDecodeError:
        logger.error("failed to parse AI response", extra={"raw": raw[:200]})
        return {
            "title": "Unparseable change",
            "summary": raw[:500],
            "severity": "medium",
        }
