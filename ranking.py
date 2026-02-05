from pydantic import BaseModel
from typing import List, Optional

class FlightOption(BaseModel):
    price: Optional[float]
    airline: str
    from_city: str
    to_city: str
    departure: str
    arrival: str
    duration_hours: float
    stop_count: int

def normalize_serpapi_result(raw) -> FlightOption:
    legs = raw["flights"]
    first = legs[0]
    last = legs[-1]

    total_minutes = raw.get("total_duration", 0)
    duration_hours = round(total_minutes / 60, 2) if total_minutes else 0.0

    airlines = {leg["airline"] for leg in legs}
    stop_count = len(legs) - 1

    price_value = raw.get("price", None)

    return FlightOption(
        price=price_value,
        airline=",".join(airlines),
        from_city=first["departure_airport"]["id"],
        to_city=last["arrival_airport"]["id"],
        departure=first["departure_airport"]["time"],
        arrival=last["arrival_airport"]["time"],
        duration_hours=duration_hours,
        stop_count=stop_count,
    )

def normalize_many(raw_list) -> List[FlightOption]:
    options = []
    for r in raw_list:
        try:
            options.append(normalize_serpapi_result(r))
        except KeyError:
            continue
    return options

def pretty_print(options: List[FlightOption]):
    for idx, o in enumerate(options):
        price_str = f"₹{o.price}" if o.price is not None else "N/A"
        print(
            f"{idx}. {o.from_city}->{o.to_city} | {o.airline} | "
            f"{price_str} | {o.duration_hours}h | {o.stop_count} stops | "
            f"{o.departure} → {o.arrival}"
        )

# ---- AI ranking (temporarily disabled) ----
# from langchain_community.chat_models import ChatOllama
# from textwrap import dedent
#
# llm = ChatOllama(model="phi3")
#
# def choose_best_option(options: List[FlightOption], preference_text: str, top_k: int = 3):
#     lines = ["ID | Airline | Price | Duration(h) | Stops | Dep -> Arr"]
#     for idx, o in enumerate(options):
#         price_str = o.price if o.price is not None else "N/A"
#         lines.append(
#             f"{idx} | {o.airline} | {price_str} | "
#             f"{o.duration_hours} | {o.stop_count} | "
#             f"{o.departure} -> {o.arrival}"
#         )
#     table = "\n".join(lines)
#
#     prompt = dedent(f"""
#     You are a travel assistant helping choose the best flight.
#
#     User preferences: {preference_text}
#
#     Here are candidate round-trip options between Indian cities:
#
#     {table}
#
#     Task:
#     - Pick the best {top_k} options (by ID).
#     - Explain clearly in bullet points why you chose them
#       (price vs duration vs stops vs times of day).
#     - End by saying: "I recommend option X as the top choice."
#
#     Keep the answer short and clear.
#     """)
#
#     response = llm.invoke(prompt)
#     return response.content

from textwrap import dedent
from langchain_community.chat_models import ChatOllama  # local LLM via Ollama. [web:107][web:109]

llm = ChatOllama(model="phi3")  # make sure `ollama pull phi3` is done. [web:113][web:116]

def choose_best_option(options: List[FlightOption], preference_text: str, top_k: int = 3) -> str:
    lines = ["ID | Airline | Price | Duration(h) | Stops | Dep -> Arr"]
    for idx, o in enumerate(options):
        price_str = o.price if o.price is not None else "N/A"
        lines.append(
            f"{idx} | {o.airline} | {price_str} | "
            f"{o.duration_hours} | {o.stop_count} | "
            f"{o.departure} -> {o.arrival}"
        )
    table = "\n".join(lines)

    prompt = dedent(f"""
    You are a travel assistant helping an Indian traveler choose flights.

    User preferences: {preference_text}

    Here are candidate round-trip options:

    {table}

    Task:
    - Pick the best {top_k} options by ID.
    - Explain in a few bullet points why they are good
      (price vs duration vs stops vs timings).
    - End with one sentence: "I recommend option X as the top choice."

    Keep the answer concise.
    """)

    resp = llm.invoke(prompt)
    return resp.content
