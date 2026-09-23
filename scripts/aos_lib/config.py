from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Sao_Paulo")
TZ_NAME = "America/Sao_Paulo"

TASK_FOLDERS = ("pending", "recurring", "completed", "obsolete", "canceled")
PROJECT_STATUSES = ("pending", "ongoing", "completed", "canceled")

UNIQUE_TYPES = frozenset({"unique-independent", "unique-project"})
RECURRING_TYPES = frozenset(
    {"recurring-independent", "recurring-project", "maintenance"}
)
ALL_TYPES = UNIQUE_TYPES | RECURRING_TYPES

UNIQUE_STATUSES = frozenset({"pending", "completed", "obsolete", "canceled"})
RECURRING_STATUSES = frozenset({"recurring", "completed", "obsolete", "canceled"})
PHASE_STATUSES = frozenset({"pending", "ongoing", "completed", "obsolete"})

WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
WEEKDAY_INDEX = {name: i for i, name in enumerate(WEEKDAYS)}

CADENCE_KINDS = frozenset({"daily", "weekdays", "interval"})
INTERVAL_UNITS = frozenset({"days", "weeks", "months"})

SECTION_OVERDUE = "Overdue"
SECTION_TODAY = "Today"
SECTION_1_DAY = "1 day"
SECTION_2_3_DAYS = "2-3 days"
SECTION_4_7_DAYS = "4-7 days"
SECTION_8_30_DAYS = "8-30 days"
SECTION_PLUS_30 = "+30 days"
SECTION_UNDEFINED = "Undefined"

BUCKET_ORDER = (
    SECTION_OVERDUE,
    SECTION_TODAY,
    SECTION_1_DAY,
    SECTION_2_3_DAYS,
    SECTION_4_7_DAYS,
    SECTION_8_30_DAYS,
    SECTION_PLUS_30,
    SECTION_UNDEFINED,
)

STATUS_FOLDER = {
    "pending": "pending",
    "recurring": "recurring",
    "completed": "completed",
    "obsolete": "obsolete",
    "canceled": "canceled",
}


def get_root() -> Path:
    env = os.environ.get("AOS_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent.parent


def today(_root: Path | None = None) -> date:
    override = os.environ.get("AOS_TODAY")
    if override:
        return date.fromisoformat(override)
    return datetime.now(TZ).date()


def user_dir(root: Path) -> Path:
    return root / "user"


def tasks_dir(root: Path) -> Path:
    return root / "user" / "tasks"


def projects_dir(root: Path) -> Path:
    return root / "user" / "projects"


def project_status(root: Path, slug: str) -> str | None:
    """Hub folder name (`pending` / `ongoing` / …), or None if missing."""
    name = (slug or "").strip()
    if not name:
        return None
    base = projects_dir(root)
    for st in PROJECT_STATUSES:
        if (base / st / name).is_dir():
            return st
    return None


def recurring_project_live(root: Path, data: dict) -> bool:
    """recurring-project runs only while the hub is ongoing.

    Independent recurrences and maintenance are always live.
    """
    t = str(data.get("type") or "").strip()
    if t != "recurring-project":
        return True
    return project_status(root, str(data.get("project") or "")) == "ongoing"


def daily_dir(root: Path) -> Path:
    return root / "user" / "daily"


def schedule_dir(root: Path) -> Path:
    return root / "user" / "schedule"


def research_dir(root: Path) -> Path:
    return root / "user" / "research"


def logs_dir(root: Path) -> Path:
    return root / "logs"
