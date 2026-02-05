from api_client import search_round_trip
from ranking import normalize_many, pretty_print

ROUTES = {
    "1": ("BLR", "DEL"),
    "2": ("DEL", "BLR"),
    "3": ("BLR", "JAI"),
    "4": ("JAI", "BLR"),
}

def run_demo():
    print("=== FLIGHT AGENT STARTED ===")

    print("Choose route:")
    print(" 1) BLR → DEL")
    print(" 2) DEL → BLR")
    print(" 3) BLR → JAI")
    print(" 4) JAI → BLR")

    choice = input("Enter 1–4: ").strip()
    if choice not in ROUTES:
        print("Invalid choice.")
        return

    origin, destination = ROUTES[choice]

    depart_date = input("Enter outbound date (YYYY-MM-DD): ").strip()
    return_date = input("Enter return date   (YYYY-MM-DD): ").strip()

    print(f"\nSearching flights {origin} → {destination} {depart_date} to {return_date}...\n")

    raw_flights = search_round_trip(origin, destination, depart_date, return_date)
    if not raw_flights:
        print("No flights found.")
        return

    options = normalize_many(raw_flights)
    if not options:
        print("No valid options after normalizing.")
        return

    print("Top options:")
    pretty_print(options[:5])

    # ---- AI recommendation (temporarily disabled) ----
    # from ranking import choose_best_option
    # prefs = (
    #     "Prefers reasonable price, avoids red-eye flights, "
    #     "okay with 1 stop but prefers non-stop, "
    #     "likes departures between 7:00 and 11:00 local time."
    # )
    # print("\nAI recommendation (local model):\n")
    # explanation = choose_best_option(options[:5], prefs)
    # print(explanation)

if __name__ == "__main__":
    run_demo()
