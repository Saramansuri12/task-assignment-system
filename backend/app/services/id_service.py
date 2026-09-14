"""
IDENTIFIER GENERATION
=====================

Several tables use a String primary key with no server-side default and
no autoincrement (tasks.task_id, projects.project_id, skills.skill_id,
assignments.assignment_id). Inserting without an explicit value fails
with a NOT NULL constraint error.

The seeded data uses zero-padded prefixes (EMP001, TASK001, PRJ001), so
new records follow the same convention and continue the sequence rather
than using random UUIDs that would look out of place next to the
imported rows.
"""

from __future__ import annotations

import re
from typing import Optional

from sqlalchemy.orm import Session


def next_identifier(
    db: Session,
    model,
    column,
    prefix: str,
    width: int = 6,
) -> str:
    """
    Find the highest numeric suffix already used for `prefix` and return
    the next one. Falls back to `prefix` + 1 when the table is empty.

    Example: TASK000001 -> TASK000002
    """

    pattern = re.compile(
        r"^" + re.escape(prefix) + r"(\d+)$"
    )

    highest = 0

    rows = (
        db.query(column)
        .filter(column.like(f"{prefix}%"))
        .all()
    )

    for (value,) in rows:

        if value is None:
            continue

        match = pattern.match(str(value))

        if match:
            highest = max(highest, int(match.group(1)))

    return f"{prefix}{highest + 1:0{width}d}"


def ensure_unique(
    db: Session,
    model,
    column,
    candidate: str,
    prefix: str,
    width: int = 6,
) -> str:
    """Guard against a collision from a concurrent insert."""

    attempts = 0

    while (
        db.query(model).filter(column == candidate).first() is not None
        and attempts < 50
    ):
        candidate = next_identifier(db, model, column, prefix, width)
        attempts += 1

    return candidate


def generate_id(
    db: Session,
    model,
    column,
    prefix: str,
    provided: Optional[str] = None,
    width: int = 6,
) -> str:
    """
    Return `provided` when the caller supplied one, otherwise generate
    the next identifier in the sequence.
    """

    if provided:
        return str(provided).strip()

    candidate = next_identifier(db, model, column, prefix, width)

    return ensure_unique(db, model, column, candidate, prefix, width)
