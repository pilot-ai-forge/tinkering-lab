import streamlit as st

from api_client import search_round_trip
from ranking import normalize_many, choose_best_option
from parsing import parse_trip_request, ParsedTripRequest


ROUTES = {
    "BLR → DEL": ("BLR", "DEL"),
    "DEL → BLR": ("DEL", "BLR"),
    "BLR → JAI": ("BLR", "JAI"),
    "JAI → BLR": ("JAI", "BLR"),
}


# --- Page and state setup ---

st.set_page_config(page_title="Flight Options Helper", layout="centered")
st.title("Flight Options Helper ✈️")

if "top_options" not in st.session_state:
    st.session_state.top_options = None
if "ai_explanation" not in st.session_state:
    st.session_state.ai_explanation = None
if "parsed_trip" not in st.session_state:
    st.session_state.parsed_trip = None


# --- Free-form / future voice entry ---

st.subheader("Describe your trip in your own words")

free_text = st.text_area(
    "Example: 'blr to del next Friday to Sunday, morning outbound, max 9000, prefer IndiGo'.",
    height=80,
)

if st.button("Parse request"):
    if not free_text.strip():
        st.warning("Please type a request first.")
    else:
        with st.spinner("Understanding your request..."):
            parsed: ParsedTripRequest = parse_trip_request(free_text)

        st.session_state.parsed_trip = parsed

        st.write("Parsed request:")
        st.json(
            {
                "origin": parsed.origin,
                "destination": parsed.destination,
                "depart_date": parsed.depart_date,
                "return_date": parsed.return_date,
                "max_price_in_inr": parsed.max_price_in_inr,
                "notes": parsed.notes,
            }
        )


parsed = st.session_state.parsed_trip

if parsed and parsed.origin and parsed.destination and parsed.depart_date and parsed.return_date:
    st.info(
        f"Parsed trip: {parsed.origin} → {parsed.destination} "
        f"{parsed.depart_date} to {parsed.return_date}"
    )

    if st.button("Search flights from parsed request"):
        st.session_state.ai_explanation = None

        st.write(
            f"Searching {parsed.origin} → {parsed.destination} "
            f"from {parsed.depart_date} to {parsed.return_date}..."
        )

        raw_flights = search_round_trip(
            parsed.origin,
            parsed.destination,
            parsed.depart_date,
            parsed.return_date,
        )

        if not raw_flights:
            st.error("No flights found for parsed request.")
            st.session_state.top_options = None
        else:
            options = normalize_many(raw_flights)
            if not options:
                st.error("No valid options after normalizing.")
                st.session_state.top_options = None
            else:
                st.session_state.top_options = options[:5]
else:
    st.info("Or use the route + date pickers below as before.")


# --- Classic route + date picker path ---

st.subheader("Manual route and dates")

route_label = st.selectbox("Route", list(ROUTES.keys()))
origin, destination = ROUTES[route_label]

depart_date = st.date_input("Outbound date")
return_date = st.date_input("Return date")

if st.button("Search flights"):
    st.session_state.ai_explanation = None

    st.write(f"Searching {origin} → {destination} from {depart_date} to {return_date}...")

    raw_flights = search_round_trip(
        origin,
        destination,
        depart_date.strftime("%Y-%m-%d"),
        return_date.strftime("%Y-%m-%d"),
    )

    if not raw_flights:
        st.error("No flights found.")
        st.session_state.top_options = None
    else:
        options = normalize_many(raw_flights)
        if not options:
            st.error("No valid options after normalizing.")
            st.session_state.top_options = None
        else:
            st.session_state.top_options = options[:5]


# --- Show results (whether from parsed or manual search) ---

top_options = st.session_state.top_options

if top_options:
    st.subheader("Top options")
    rows = []
    for idx, o in enumerate(top_options):
        rows.append(
            {
                "ID": idx,
                "From": o.from_city,
                "To": o.to_city,
                "Airline": o.airline,
                "Price (INR)": o.price,
                "Duration (h)": o.duration_hours,
                "Stops": o.stop_count,
                "Departure": o.departure,
                "Arrival": o.arrival,
            }
        )
    st.table(rows)

    prefs = (
        "Prefers reasonable price, avoids red-eye flights, "
        "okay with 1 stop but prefers non-stop, "
        "likes departures between 7:00 and 11:00 local time."
    )

    if st.button("Ask AI for recommendation"):
        with st.spinner("Thinking with local AI..."):
            st.session_state.ai_explanation = choose_best_option(top_options, prefs)

    if st.session_state.ai_explanation:
        st.subheader("AI recommendation")
        st.write(st.session_state.ai_explanation)
else:
    st.info("Search for flights to see options and AI recommendations.")
