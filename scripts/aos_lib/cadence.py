from __future__ import annotations

import calendar
from datetime import date, timedelta
from typing import Any, Iterator

from .config import INTERVAL_UNITS, RECURRING_TYPES, WEEKDAY_INDEX
from .yamlfm import as_date, as_date_list


def add_months(d: date, months: int) -> date:
    month0 = d.month - 1 + months
    year = d.year + month0 // 12
    month = month0 % 12 + 1
    last = calendar.monthrange(year, month)[1]
    return date(year, month, min(d.day, last))


def add_interval(anchor: date, steps: int, every: int, unit: str) -> date:
    n = steps * every
    if unit == "days":
        return anchor + timedelta(days=n)
    if unit == "weeks":
        return anchor + timedelta(weeks=n)
    if unit == "months":
        return add_months(anchor, n)
    raise ValueError(f"invalid interval unit: {unit}")


def until_date(data: dict[str, Any]) -> date | None:
    return as_date(data.get("until"))


def due_date(data: dict[str, Any]) -> date | None:
    return as_date(data.get("due"))


def done_count(data: dict[str, Any], d: date) -> int:
    return sum(1 for x in as_date_list(data.get("done_on") or []) if x == d)


def day_complete(data: dict[str, Any], d: date) -> bool:
    return done_count(data, d) >= 1


def cadence_of(data: dict[str, Any]) -> dict[str, Any]:
    cad = data.get("cadence") or {}
    if not isinstance(cad, dict):
        return {}
    return cad


def series_live(data: dict[str, Any]) -> bool:
    """Maintenance always. Recurring only after the first check (status ongoing)."""
    t = str(data.get("type") or "").strip()
    if t not in RECURRING_TYPES:
        return True
    return str(data.get("status") or "").strip() == "ongoing"


def within_until(d: date, data: dict[str, Any]) -> bool:
    u = until_date(data)
    if u is None:
        return True
    return d <= u


def weekday_names(cad: dict[str, Any]) -> set[str]:
    days = cad.get("days") or []
    if not isinstance(days, list):
        return set()
    out = set()
    for item in days:
        name = str(item).strip().lower()[:3]
        if name in WEEKDAY_INDEX:
            out.add(name)
    return out


def occurs_on(data: dict[str, Any], d: date) -> bool:
    if not series_live(data):
        return False
    if not within_until(d, data):
        return False
    cad = cadence_of(data)
    kind = str(cad.get("kind") or "").strip().lower()
    if kind == "daily":
        return True
    if kind == "weekdays":
        names = weekday_names(cad)
        wanted = {WEEKDAY_INDEX[n] for n in names}
        return d.weekday() in wanted
    if kind == "interval":
        return _interval_occurs(cad, d)
    return False


def _interval_occurs(cad: dict[str, Any], d: date) -> bool:
    anchor = as_date(cad.get("anchor"))
    every = cad.get("every")
    unit = str(cad.get("unit") or "").strip().lower()
    if anchor is None or not isinstance(every, int) or every < 1:
        return False
    if unit not in INTERVAL_UNITS:
        return False
    if d < anchor:
        return False
    n = 0
    while n < 100000:
        cur = add_interval(anchor, n, every, unit)
        if cur == d:
            return True
        if cur > d:
            return False
        n += 1
    return False


def _interval_from(cad: dict[str, Any], start: date) -> Iterator[date]:
    anchor = as_date(cad.get("anchor"))
    every = cad.get("every")
    unit = str(cad.get("unit") or "").strip().lower()
    if anchor is None or not isinstance(every, int) or every < 1:
        return
    if unit not in INTERVAL_UNITS:
        return
    n = 0
    while n < 100000:
        cur = add_interval(anchor, n, every, unit)
        n += 1
        if cur < start:
            continue
        yield cur
        if cur.year > start.year + 80:
            return


def next_occurrence(data: dict[str, Any], start: date) -> date | None:
    """First cadence day on or after start that is not already done, within until."""
    if not series_live(data):
        return None
    cad = cadence_of(data)
    kind = str(cad.get("kind") or "").strip().lower()
    if kind == "daily":
        d = start
        for _ in range(40000):
            if not within_until(d, data):
                return None
            if not day_complete(data, d):
                return d
            d += timedelta(days=1)
        return None
    if kind == "weekdays":
        names = weekday_names(cad)
        wanted = {WEEKDAY_INDEX[n] for n in names}
        if not wanted:
            return None
        d = start
        for _ in range(40000):
            if not within_until(d, data):
                return None
            if d.weekday() in wanted and not day_complete(data, d):
                return d
            d += timedelta(days=1)
        return None
    if kind == "interval":
        for cur in _interval_from(cad, start):
            if not within_until(cur, data):
                return None
            if not day_complete(data, cur):
                return cur
        return None
    return None


def index_dates(data: dict[str, Any], today: date) -> list[date]:
    """At most two dates: today (if due now) and the next date > today."""
    out: list[date] = []
    if occurs_on(data, today) and not day_complete(data, today):
        out.append(today)
    nxt = next_occurrence(data, today + timedelta(days=1))
    if nxt is not None:
        out.append(nxt)
    return out
