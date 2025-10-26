import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from agent import run_agent_on_syllabus
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def get_chat_model():
    return ChatGoogleGenerativeAI(api_key=GOOGLE_API_KEY, model="gemini-2.0-flash-lite", temperature=0.2)

def plan_schedule(syllabus_items: List[Dict[str, Any]], existing_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Plan a study schedule using an LLM and existing calendar events.
    Returns a list of JSON-serializable study blocks:
    [
        {"title": str, "topics": List[str], "start": ISO string, "end": ISO string}
    ]
    """
    scheduled_blocks = []
    now = datetime.now(timezone.utc)

    # collect the busy slots from existing events
    busy_slots = []
    for ev in existing_events:
        start = ev.get("start", {}).get("dateTime")
        end = ev.get("end", {}).get("dateTime")
        if start and end:
            try:
                busy_slots.append((datetime.fromisoformat(start), datetime.fromisoformat(end)))
            except Exception:
                continue

    # syllabus items iteration
    model = get_chat_model()
    for item in syllabus_items:
        # generate a study block title and topics using LLM
        try:
            prompt = f"""
You are a study planner AI. Generate a concise study session title and a list of topics
for the following syllabus item. Return a JSON object with "title" and "topics" keys.

Syllabus item raw text:
{item.get("raw", "")}
"""
            system_msg = SystemMessage(content="You are a helpful study planner AI.")
            human_msg = HumanMessage(content=prompt)
            response = model([system_msg, human_msg])
            # Ensure response is valid JSON
            import json
            try:
                data = json.loads(response.content)
                title = data.get("title", item.get("kind", "Study Session"))
                topics = data.get("topics", [])
            except Exception:
                title = item.get("kind", "Study Session")
                topics = item.get("topics", [])
        except Exception:
            title = item.get("kind", "Study Session")
            topics = item.get("topics", [])

        # schedule block: pick a free slot in the next 7 days
        block_duration = timedelta(hours=2)  # default 2 hours per study block
        start_time = now + timedelta(days=1)
        end_time = start_time + block_duration

        # ensure no conflict with existing events
        for busy_start, busy_end in busy_slots:
            if start_time < busy_end and end_time > busy_start:
                start_time = busy_end + timedelta(minutes=15)
                end_time = start_time + block_duration

        scheduled_blocks.append({
            "title": title,
            "topics": topics,
            "start": start_time.isoformat(),
            "end": end_time.isoformat()
        })

        # update now for next block
        now = end_time

    return scheduled_blocks
