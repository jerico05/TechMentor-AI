"""Compute total professional experience from LinkedIn experience entries."""

from __future__ import annotations

import re
from datetime import date
from typing import NamedTuple

_MONTHS_EN = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

_MONTHS_FR = {
    "janv": 1,
    "janvier": 1,
    "fev": 2,
    "fevr": 2,
    "févr": 2,
    "fevrier": 2,
    "février": 2,
    "mars": 3,
    "avr": 4,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juil": 7,
    "juillet": 7,
    "aout": 8,
    "août": 8,
    "sept": 9,
    "septembre": 9,
    "oct": 10,
    "octobre": 10,
    "nov": 11,
    "novembre": 11,
    "dec": 11,
    "déc": 11,
    "decembre": 12,
    "décembre": 12,
}

_MONTHS = {**_MONTHS_EN, **_MONTHS_FR}

_PRESENT_MARKERS = (
    "present",
    "présent",
    "aujourd",
    "actuel",
    "current",
    "now",
    "ce jour",
)


class _Interval(NamedTuple):
    start: date
    end: date


def _is_present(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _PRESENT_MARKERS)


def _parse_month_token(token: str) -> int | None:
    cleaned = re.sub(r"[^a-zàâäéèêëïîôùûüç]", "", token.lower())
    return _MONTHS.get(cleaned)


def _parse_year_token(token: str) -> int | None:
    match = re.search(r"(20\d{2}|19\d{2})", token)
    if not match:
        return None
    return int(match.group(1))


def _parse_month_year(text: str) -> tuple[int, int] | None:
    stripped = text.strip()
    if not stripped:
        return None

    year_only = re.fullmatch(r"(20\d{2}|19\d{2})", stripped)
    if year_only:
        return 1, int(year_only.group(1))

    match = re.search(
        r"([a-zàâäéèêëïîôùûüç.]+)?\s*(20\d{2}|19\d{2})",
        stripped,
        re.I,
    )
    if not match:
        return None

    month = _parse_month_token(match.group(1) or "") or 1
    year = int(match.group(2))
    return month, year


def _to_date(month: int, year: int) -> date:
    month = min(max(month, 1), 12)
    return date(year, month, 1)


def _parse_duration_count(duration: str) -> int | None:
    """Parse '2 years 3 months', '18 mois', '1 an', etc. Returns total months."""
    text = duration.lower()
    years = 0
    months = 0

    year_match = re.search(r"(\d+)\s*(?:years?|ans?|yrs?)", text)
    if year_match:
        years = int(year_match.group(1))

    month_match = re.search(r"(\d+)\s*(?:months?|mois|mos?)", text)
    if month_match:
        months = int(month_match.group(1))

    if years or months:
        return years * 12 + months
    return None


def _parse_date_range(duration: str) -> _Interval | None:
    if not duration or not duration.strip():
        return None

    text = duration.strip()

    # Explicit duration without dates: "2 ans 6 mois"
    counted = _parse_duration_count(text)
    if counted and not re.search(r"(20\d{2}|19\d{2})", text):
        end = date.today()
        start_year = end.year - counted // 12
        start_month = end.month - (counted % 12)
        if start_month <= 0:
            start_month += 12
            start_year -= 1
        return _Interval(_to_date(start_month, start_year), end)

    parts = re.split(r"\s*(?:-|–|—|to|à|au|jusqu)\s*", text, maxsplit=1, flags=re.I)
    if len(parts) == 1:
        parts = re.split(r"\s+", text, maxsplit=1)

    start_part = parts[0].strip()
    end_part = parts[1].strip() if len(parts) > 1 else ""

    start_parsed = _parse_month_year(start_part)
    if not start_parsed:
        return None

    start = _to_date(*start_parsed)

    if not end_part or _is_present(end_part):
        return _Interval(start, date.today())

    end_parsed = _parse_month_year(end_part)
    if not end_parsed:
        counted = _parse_duration_count(end_part)
        if counted:
            end_year = start.year + counted // 12
            end_month = start.month + (counted % 12)
            if end_month > 12:
                end_month -= 12
                end_year += 1
            return _Interval(start, _to_date(end_month, end_year))
        return None

    end = _to_date(*end_parsed)
    if end < start:
        return None
    return _Interval(start, end)


def _merge_intervals(intervals: list[_Interval]) -> list[_Interval]:
    if not intervals:
        return []

    sorted_intervals = sorted(intervals, key=lambda i: i.start)
    merged: list[_Interval] = [sorted_intervals[0]]

    for current in sorted_intervals[1:]:
        last = merged[-1]
        if current.start <= last.end:
            merged[-1] = _Interval(last.start, max(last.end, current.end))
        else:
            merged.append(current)

    return merged


def _months_between(start: date, end: date) -> int:
    return max(0, (end.year - start.year) * 12 + (end.month - start.month) + 1)


def compute_total_experience_years(experiences: list[dict] | None) -> float:
    """Sum employment periods from LinkedIn experiences (merged if overlapping)."""
    if not experiences:
        return 0.0

    intervals: list[_Interval] = []
    for exp in experiences:
        if not isinstance(exp, dict):
            continue

        duration = str(exp.get("duration") or "").strip()
        if not duration:
            continue

        interval = _parse_date_range(duration)
        if interval:
            intervals.append(interval)

    if not intervals:
        return 0.0

    total_months = sum(_months_between(i.start, i.end) for i in _merge_intervals(intervals))
    return round(total_months / 12, 1)
