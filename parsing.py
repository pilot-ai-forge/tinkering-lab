from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from textwrap import dedent
from datetime import datetime, timedelta
import json

import dateparser
from langchain_community.chat_models import ChatOllama  # local model via Ollama. [web:107][web:109]


@dataclass
class ParsedTripRequest:
    origin: Optional[str]
    destination: Optional[str]
    depart_date: Optional[str]     # "YYYY-MM-DD"
    return_date: Optional[str]     # "YYYY-MM-DD"
    max_price_in_inr: Optional[int]
    notes: str                     # extra preferences or fallback text


from datetime import datetime, timedelta

def _parse_date_to_iso(text: str) -> Optional[str]:
    if not text:
        return None
    
    text_lower = text.lower().strip()
    today = datetime.now()
    
    # Handle common relative day names
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    
    # Try "next Monday", "next Tuesday", etc.
    for day_name, day_num in weekdays.items():
        if day_name in text_lower:
            current_weekday = today.weekday()
            days_ahead = (day_num - current_weekday) % 7
            
            # If user says "next Tuesday" and today is Monday, they mean tomorrow (1 day)
            # But if today IS Tuesday, "next Tuesday" means 7 days ahead
            if "next" in text_lower:
                if days_ahead == 0:
                    days_ahead = 7
                elif days_ahead < 0:
                    days_ahead += 7
            elif "this" in text_lower:
                if days_ahead == 0:
                    days_ahead = 0  # today
            else:
                # No "next" or "this", assume next occurrence
                if days_ahead == 0:
                    days_ahead = 7
            
            target_date = today + timedelta(days=days_ahead)
            return target_date.strftime("%Y-%m-%d")
    
    # Handle "tomorrow"
    if "tomorrow" in text_lower:
        target_date = today + timedelta(days=1)
        return target_date.strftime("%Y-%m-%d")
    
    # Handle "today"
    if "today" in text_lower:
        return today.strftime("%Y-%m-%d")
    
    # Fallback: try dateparser for absolute dates like "2026-02-10" or "Feb 10"
    dt = dateparser.parse(text, settings={'PREFER_DATES_FROM': 'future'})
    if dt:
        return dt.strftime("%Y-%m-%d")
    
    return None

llm = ChatOllama(model="phi3")  # make sure you have `ollama pull phi3` done. [web:107]

def parse_trip_request(user_text: str) -> ParsedTripRequest:
    """
    Use a local LLM to turn a free-form request into structured fields
    your flight agent can use.
    """

    system_prompt = dedent("""
    You are a JSON converter for flight search requests.

    CRITICAL RULES:
    1. Output ONLY a single JSON object, nothing else.
    2. Do NOT add comments (no // or /* */).
    3. Do NOT add any text before or after the JSON.
    4. Do NOT use markdown fences.
    5. Always use these exact keys:
       - origin
       - destination
       - depart_date_text
       - return_date_text
       - max_price_in_inr
       - notes

    FIELD RULES:
    - origin, destination: 3-letter IATA codes (BLR, DEL, BOM, etc.)
    - depart_date_text: short phrase like "next Tuesday", "Feb 10", "tomorrow"
    - return_date_text: same format; if user says "Tuesday to Thursday", 
      depart is Tuesday, return is Thursday.
    - max_price_in_inr: integer if user says a number like "max 21000" or "under 15000";
      otherwise null.
    - notes: summarize preferences (time, airlines, etc.)

    EXAMPLE INPUT:
    "blr to del next Tuesday to Thursday max price 21000 preferred akasa air india"

    CORRECT OUTPUT:
    {
      "origin": "BLR",
      "destination": "DEL",
      "depart_date_text": "next Tuesday",
      "return_date_text": "next Thursday",
      "max_price_in_inr": 21000,
      "notes": "Prefers Akasa Air and Air India."
    }

    Now convert this request:
    """)

    user_prompt = f"User request: {user_text}"
    prompt = system_prompt + "\n\n" + user_prompt

    raw = llm.invoke(prompt)
    raw_text = raw.content if hasattr(raw, "content") else str(raw)
    txt = raw_text.strip()

    print("===== RAW MODEL OUTPUT =====")
    print(txt)
    print("===== END =====")

    # 1) Strip code fences aggressively
    if "```" in txt:
        # Remove everything before first ``` and after last ```
        start = txt.find("```")
        end = txt.rfind("```")
        if start != -1 and end != -1 and end > start:
            txt = txt[start+3:end].strip()
            # Also remove language hint like "json" if it's on its own line
            if txt.startswith("json"):
                txt = txt[4:].strip()

    # 2) Extract ONLY the first {...} block (ignoring text after the closing brace)
    import re
    m = re.search(r"\{[^\}]*\}", txt, re.DOTALL)
    if m:
        candidate = m.group(0)
    else:
        candidate = txt

    # 3) Remove any // ... comments and clean up trailing commas
    candidate = re.sub(r"//[^\n]*", "", candidate)  # strip comments
    candidate = re.sub(r",(\s*[}\]])", r"\1", candidate)  # fix trailing commas before } or ]

    import json
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as e:
        # Fallback: keep everything in notes
        return ParsedTripRequest(
            origin=None,
            destination=None,
            depart_date=None,
            return_date=None,
            max_price_in_inr=None,
            notes=raw_text.strip(),
        )

    origin = data.get("origin")
    destination = data.get("destination")
    depart_date_text = data.get("depart_date_text")
    return_date_text = data.get("return_date_text")
    max_price = data.get("max_price_in_inr")
    notes = data.get("notes") or ""

    depart_iso = _parse_date_to_iso(depart_date_text) if depart_date_text else None
    return_iso = _parse_date_to_iso(return_date_text) if return_date_text else None

    return ParsedTripRequest(
        origin=origin,
        destination=destination,
        depart_date=depart_iso,
        return_date=return_iso,
        max_price_in_inr=max_price,
        notes=notes.strip(),
    )
