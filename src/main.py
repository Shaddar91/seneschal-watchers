import asyncio
import logging
import sys
from pythonjsonlogger import json as json_log

from .config import settings
from .db import get_active_sources, get_latest_snapshot, save_snapshot, save_change, close_pool
from .page_saver import fetch_page
from .differ import compute_diff
from .processor import extract_change

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = json_log.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)
    logging.root.setLevel(settings.log_level)


async def check_source(source: dict) -> None:
    source_id = source["id"]
    url = source["url"]
    name = source.get("name", url)

    logger.info("checking source", extra={"source_id": source_id, "name": name})

    try:
        current_content = await fetch_page(url)
    except Exception as e:
        logger.error("failed to fetch page", extra={"source_id": source_id, "error": str(e)})
        return

    previous_content = await get_latest_snapshot(source_id)
    await save_snapshot(source_id, current_content)

    if previous_content is None:
        logger.info("first snapshot saved", extra={"source_id": source_id})
        return

    diff_text = compute_diff(previous_content, current_content)
    if diff_text is None:
        logger.info("no changes detected", extra={"source_id": source_id})
        return

    logger.info("change detected", extra={"source_id": source_id})

    extracted = await extract_change(diff_text)
    await save_change(
        source_id=source_id,
        title=extracted.get("title", "Unknown change"),
        summary=extracted.get("summary", ""),
        severity=extracted.get("severity", "medium"),
        raw_diff=diff_text,
    )
    logger.info("change saved", extra={"source_id": source_id, "title": extracted.get("title")})


async def run_cycle() -> None:
    sources = await get_active_sources()
    logger.info("cycle start", extra={"source_count": len(sources)})
    for source in sources:
        await check_source(source)
    logger.info("cycle complete")


async def main() -> None:
    setup_logging()
    logger.info("seneschal-watchers starting", extra={"poll_interval": settings.poll_interval_seconds})

    try:
        while True:
            await run_cycle()
            await asyncio.sleep(settings.poll_interval_seconds)
    except KeyboardInterrupt:
        logger.info("shutting down")
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
