import os
import re
import json
from typing import List, Dict, Any
from dateutil import parser as dateparser
from datetime import datetime, timedelta, timezone

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.agents import initialize_agent, Tool, AgentType


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# regex extract 
DATE_REGEX = r'((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|' \
             r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[\w\s,.-]*\d{1,2}(?:,\s*\d{4})?)' \
             r'|(\d{4}-\d{2}-\d{2})|(\d{1,2}/\d{1,2}/\d{2,4})'

def heuristically_extract_items(text: str) -> List[Dict[str, Any]]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    items = []
    id_counter = 0
    keywords = r'\b(Assignment|Homework|Exam|Quiz|Project|Midterm|Final|Lab)\b'

    for i, line in enumerate(lines):
        if re.search(keywords, line, flags=re.I):
            block = " ".join(lines[i:i+3])
            m = re.search(DATE_REGEX, block, flags=re.I)
            due_iso = None
            if m:
                date_str = next(g for g in m.groups() if g)
                try:
                    parsed_dt = dateparser.parse(date_str, fuzzy=True)
                    if parsed_dt and parsed_dt.tzinfo is None:
                        parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
                    due_iso = parsed_dt.isoformat()
                except Exception:
                    pass

            kind = "Assignment" if re.search(r'Assignment|Homework|Project|Lab', line, re.I) else \
                   "Exam" if re.search(r'Exam|Midterm|Final|Quiz', line, re.I) else "other"

            items.append({
                "id": f"item_{id_counter}",
                "kind": kind,
                "raw": block,
                "due": due_iso,
                "topics": []
            })
            id_counter += 1
    return items

# llms plus agent tooling
def get_chat_model():
    return ChatGoogleGenerativeAI(api_key=GOOGLE_API_KEY, model="gemini-2.0-flash-lite", temperature=0.2)

def tool_parse_syllabus(raw_text: str) -> str:
    return json.dumps(heuristically_extract_items(raw_text))

def tool_generate_topics(item_raw: str) -> str:
    model = get_chat_model()
    system = SystemMessage(content="Return a JSON object {\"topics\": [..]} of concise study topics.")
    prompt = f"Syllabus snippet:\n{item_raw}\n\nRespond with JSON only."
    resp = model([system, HumanMessage(content=prompt)])
    text = getattr(resp, "content", str(resp))
    try:
        return json.dumps(json.loads(text))
    except Exception:
        match = re.search(r'\{.*\}', text, re.S)
        if match:
            return match.group(0)
        return json.dumps({"topics": [item_raw[:50]]})

# run agent
def run_agent_on_syllabus(raw_text: str) -> List[Dict[str, Any]]:
    model = get_chat_model()
    tools = [
        Tool(name="parse_syllabus", func=lambda t: tool_parse_syllabus(t), description="Parse syllabus text"),
        Tool(name="generate_topics", func=lambda t: tool_generate_topics(t), description="Generate study topics")
    ]

    agent = initialize_agent(tools, model, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False)

    result = agent.run(f"Parse syllabus into structured JSON. Use parse_syllabus tool.\n\n{raw_text}")
    try:
        items = json.loads(result)
    except Exception:
        items = heuristically_extract_items(raw_text)

    for it in items:
        if not it.get("topics"):
            try:
                topics = json.loads(tool_generate_topics(it["raw"]))
                it["topics"] = topics.get("topics", [])
            except Exception:
                it["topics"] = []
    return items
