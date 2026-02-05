import requests
from config import SERPAPI_KEY, SERPAPI_ENDPOINT, DEFAULT_CURRENCY

def search_round_trip(origin, destination, depart_date, return_date):
    """
    origin/destination: IATA codes like 'BLR', 'DEL'
    dates: '2026-03-10' format (yyyy-mm-dd)
    """
    if not SERPAPI_KEY:
        raise RuntimeError("SERPAPI_KEY not set in .env")

    params = {
        "engine": "google_flights",
        # type omitted: default is 1 = round trip. [web:38]
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": depart_date,   # YYYY-MM-DD. [web:38]
        "return_date": return_date,     # YYYY-MM-DD. [web:38]
        "currency": DEFAULT_CURRENCY,
        "api_key": SERPAPI_KEY,
    }

    resp = requests.get(SERPAPI_ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    best = data.get("best_flights", [])
    other = data.get("other_flights", [])
    return best + other
