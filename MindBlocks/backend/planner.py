from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from dateutil import parser as dateparser

def compute_free_slots(existing_events: List[Dict[str, Any]],
                       window_start: datetime,
                       window_end: datetime,
                       min_block_minutes: int = 30) -> List[Dict[str, datetime]]:
    """
    Compute available free slots between existing calendar events.
    Returns list of dicts {"start": dt, "end": dt}.
    """
    evs = []
    for ev in existing_events:
        s = ev.get("start")
        e = ev.get("end")
        if isinstance(s, str):
            s = dateparser.parse(s)
        if isinstance(e, str):
            e = dateparser.parse(e)
        if s.tzinfo is None:
            s = s.replace(tzinfo=timezone.utc)
        if e.tzinfo is None:
            e = e.replace(tzinfo=timezone.utc)
        # discard events completely outside window
        if e <= window_start or s >= window_end:
            continue
        evs.append({"start": max(s, window_start), "end": min(e, window_end)})

    evs.sort(key=lambda x: x["start"])
    free_slots = []
    cursor = window_start

    for ev in evs:
        if ev["start"] > cursor:
            free_slots.append({"start": cursor, "end": ev["start"]})
        cursor = max(cursor, ev["end"])

    if cursor < window_end:
        free_slots.append({"start": cursor, "end": window_end})

    # filter slots smaller than min_block_minutes
    min_delta = timedelta(minutes=min_block_minutes)
    free_slots = [fs for fs in free_slots if (fs["end"] - fs["start"]) >= min_delta]
    return free_slots


def allocate_study_blocks(items: List[Dict[str, Any]],
                          free_slots: List[Dict[str, datetime]],
                          now: datetime = None,
                          per_assignment_hours: float = 3.0,
                          session_length_minutes: int = 60) -> List[Dict[str, Any]]:
    """
    Allocate study blocks for syllabus items in available free slots.
    - items: list of syllabus items, each with 'id', 'due', 'raw', 'topics'.
    - free_slots: list of free time intervals (from compute_free_slots)
    Returns list of planned events with 'start', 'end', 'title', 'description', 'for_item_id', 'topics'.
    """
    now = now or datetime.now(timezone.utc)
    planned = []

    # make a mutable copy of free_slots
    slots = [{"start": fs["start"], "end": fs["end"]} for fs in free_slots]

    # sort items by due date ascending
    items_sorted = sorted([it for it in items if it.get("due")],
                          key=lambda x: dateparser.parse(x["due"]))

    for it in items_sorted:
        due_dt = dateparser.parse(it["due"])
        if due_dt.tzinfo is None:
            due_dt = due_dt.replace(tzinfo=timezone.utc)

        # determine number of sessions
        total_minutes = int(per_assignment_hours * 60)
        session_minutes = session_length_minutes
        sessions_needed = max(1, total_minutes // session_minutes)
        remainder = total_minutes - sessions_needed * session_minutes
        if remainder > 0:
            sessions_needed += 1

        session_lengths = [session_minutes] * sessions_needed
        if remainder > 0:
            session_lengths[-1] = session_lengths[-1] - (session_minutes - remainder)

        for sl in session_lengths:
            length = timedelta(minutes=sl)
            allocated = False
            # iterate slots from latest to earliest (prefer closer to due date)
            for idx in range(len(slots)-1, -1, -1):
                slot = slots[idx]
                if slot["start"] >= due_dt:
                    continue
                candidate_end = min(slot["end"], due_dt)
                candidate_start = candidate_end - length
                if candidate_start < slot["start"]:
                    continue
                if candidate_end <= now:
                    continue
                if candidate_start < now:
                    candidate_start = now
                    candidate_end = candidate_start + length
                    if candidate_end > slot["end"] or candidate_end > due_dt:
                        continue
                # allocate session
                planned.append({
                    "title": f"Study: {it.get('kind','').title()} - {it['id']}",
                    "description": it.get("raw", ""),
                    "start": candidate_start.isoformat(),
                    "end": candidate_end.isoformat(),
                    "for_item_id": it["id"],
                    "topics": it.get("topics", [])
                })
                # adjust slot
                if candidate_start <= slot["start"] and candidate_end >= slot["end"]:
                    slots.pop(idx)
                elif candidate_start <= slot["start"]:
                    slots[idx]["start"] = candidate_end
                elif candidate_end >= slot["end"]:
                    slots[idx]["end"] = candidate_start
                else:
                    old_end = slot["end"]
                    slots[idx]["end"] = candidate_start
                    slots.insert(idx+1, {"start": candidate_end, "end": old_end})
                allocated = True
                break
            if not allocated:
                # could not allocate this session
                continue

    planned.sort(key=lambda x: x["start"])
    return planned
