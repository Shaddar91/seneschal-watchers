from dataclasses import dataclass
from datetime import datetime


@dataclass
class PageSnapshot:
    source_id: int
    url: str
    content: str
    fetched_at: datetime


@dataclass
class PageDiff:
    source_id: int
    url: str
    previous_content: str
    current_content: str
    diff_text: str
    detected_at: datetime


@dataclass
class ExtractedChange:
    source_id: int
    title: str
    summary: str
    severity: str
    raw_diff: str
    detected_at: datetime
