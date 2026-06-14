import asyncpg
from .config import settings


_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(settings.database_url)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def get_active_sources() -> list[dict]:
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT id, url, name FROM regulatory_sources WHERE active = true"
    )
    return [dict(r) for r in rows]


async def get_latest_snapshot(source_id: int) -> str | None:
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT content FROM page_snapshots WHERE source_id = $1 ORDER BY fetched_at DESC LIMIT 1",
        source_id,
    )
    return row["content"] if row else None


async def save_snapshot(source_id: int, content: str) -> None:
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO page_snapshots (source_id, content, fetched_at) VALUES ($1, $2, NOW())",
        source_id,
        content,
    )


async def save_change(source_id: int, title: str, summary: str, severity: str, raw_diff: str) -> None:
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO regulatory_changes (source_id, title, summary, severity, raw_diff, detected_at) VALUES ($1, $2, $3, $4, $5, NOW())",
        source_id,
        title,
        summary,
        severity,
        raw_diff,
    )
