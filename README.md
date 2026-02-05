# Flight Booking Agent Pilot

An AI-powered flight booking agent that searches flights, ranks options, and helps users pick the best itinerary via conversational interaction.

## Problem

Booking flights involves juggling multiple tabs, filters, and trade-offs (price vs. duration vs. layovers). This agent streamlines that by handling search, comparison, and recommendation in a single conversational interface.

## What this agent does

- Understands natural-language travel requests (dates, cities, constraints).
- Calls flight search APIs to fetch itineraries.
- Scores and ranks options based on configurable criteria (price, duration, stops, etc.).
- Explains trade-offs and recommends 2–3 best options.

## Demo


<img width="947" height="521" alt="image" src="https://github.com/user-attachments/assets/3c22510a-c078-4e6c-8c59-c78c818d8222" />

<img width="967" height="661" alt="image" src="https://github.com/user-attachments/assets/26b74642-a8c7-43cc-a41d-0c45269d8ed4" />

<img width="1141" height="406" alt="image" src="https://github.com/user-attachments/assets/62d208d8-443c-456a-81fb-683d9ca4d739" />


## Architecture

- **Agent core (`agent.py`)** – Orchestrates the conversation and tool calls.
- **API client (`api_client.py`)** – Connects to the flight search API(s).
- **Ranking module (`ranking.py`)** – Scores and ranks candidate itineraries.
- **Parsing module (`parsing.py`)** – Normalizes user inputs (dates, locations, budgets).
- **Config (`config.py`)** – API keys, model configuration, ranking weights, and feature flags.
- **App entrypoint (`app.py`)** – CLI / web entry (e.g., Streamlit/FastAPI/Gradio).

<img width="2752" height="1536" alt="flight agent architecture" src="https://github.com/user-attachments/assets/a1ef349f-6cec-4d17-8999-4adee26f629b" />


## Setup

### Prerequisites

- Python 3.10+ installed
- A flight search API key (e.g., Amadeus, Skyscanner, etc.)
- An LLM provider key (if applicable), e.g., OpenAI

### Install dependencies

```bash
git clone https://github.com/pilot-ai-forge/tinkering-lab.git
cd tinkering-lab
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

Create a .env file in the project root:
FLIGHT_API_KEY=your_key_here
FLIGHT_API_BASE_URL=...
LLM_API_KEY=your_key_here
LLM_MODEL_NAME=gpt-4.1


***

## 6. How to Run

```markdown
## Usage

### Run the agent locally

```bash
python app.py


***

## 7. Configuration & Customization

```markdown
## Configuration

You can tweak behavior via `config.py`:

- **Ranking weights** – Change how much we value price vs duration vs stops.
- **Airlines / alliances** – Set preferred/blocked airlines.
- **Time windows** – Avoid red-eyes, enforce arrival/departure windows.
- **LLM model** – Swap between models via a single config entry.

> See `config.py` and inline comments for details.

## Roadmap

- [ ] Add support for multi‑city itineraries.
- [ ] Add hotel / stay suggestions from a second provider.
- [ ] Add memory of user preferences (airlines, seats, layover tolerance).
- [ ] Expose a simple web UI (Streamlit / Next.js frontend).
- [ ] Add tests for ranking and parsing logic.

## Limitations

- This is a tinkering project, not production-grade code.
- Recommendations depend on the external flight API’s data freshness and coverage.
- Prices and availability may change by the time the user books.

> Always verify final prices and details on the actual booking site.

## Contributing / Hacking

This is a playground repo. Feel free to:

- Fork the project and experiment with new ranking strategies.
- Plug in different flight APIs.
- Try different LLMs / tools for parsing and reasoning.

PRs and issues are welcome.

