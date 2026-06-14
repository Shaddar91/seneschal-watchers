import difflib
import logging

logger = logging.getLogger(__name__)


def compute_diff(previous: str, current: str) -> str | None:
    """Compute unified diff between two page snapshots.

    Returns the diff string if there are changes, None if identical.
    """
    if previous == current:
        return None

    diff_lines = difflib.unified_diff(
        previous.splitlines(keepends=True),
        current.splitlines(keepends=True),
        fromfile="previous",
        tofile="current",
        lineterm="",
    )
    diff_text = "\n".join(diff_lines)

    if not diff_text.strip():
        return None

    logger.info("diff computed", extra={"diff_length": len(diff_text)})
    return diff_text
