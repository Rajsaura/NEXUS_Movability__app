## Smart Commute Chennai — [Live Demo](https://nexus-movability-app-red.vercel.app/)

### A Multi-Modal Commute Decision Platform for Chennai

Smart Commute Chennai is a transportation decision-support web application that helps commuters choose a suitable way to travel across Chennai. Instead of simply finding a route, the application compares transportation modes based on travel time, estimated cost, estimated CO2 emissions, and user-selected priorities, then scores and ranks the options to recommend the one that best matches the commuter's preference.

> The goal is simple: help commuters make a smarter transportation decision by comparing time, cost, and environmental impact in one place.

---

## Table of Contents

- [Problem](#problem)
- [Solution](#solution)
- [Features](#features)
- [Recommendation Engine](#recommendation-engine)
- [Methodology](#methodology)
- [APIs and External Services](#apis-and-external-services)
- [Data Sources and Provenance](#data-sources-and-provenance)
- [Technology Stack](#technology-stack)
- [How the Website Works](#how-the-website-works)
- [Example Journey](#example-journey)
- [Project Architecture](#project-architecture)
- [Local Development](#local-development)
- [Testing](#testing)
- [Current Limitations](#current-limitations)
- [Data Transparency](#data-transparency)
- [Development Philosophy](#development-philosophy)
- [Future Plans](#future-plans)
- [Vision](#vision)
- [Project Status](#project-status)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## Problem

Daily commuters often make transportation decisions based primarily on travel time. However, the fastest option is not always the most practical one. For example:

- A bike may be faster but more expensive.
- A bus may be cheaper but slower.
- Metro may take slightly longer but have a lower estimated environmental impact.

This creates a multi-objective transportation decision problem. Smart Commute Chennai attempts to answer:

> "Which transportation option is best for this journey, based on what the commuter actually cares about?"

Instead of simply showing routes, the application compares the available options and explains the recommendation.

---

## Solution

The application currently focuses on three transportation modes:

| Transport Mode | Travel Time | Cost | CO2 | Route Information |
|---|---|---|---|---|
| Bike | Yes | Yes | Yes | Road routing |
| Chennai Metro | Yes | Yes | Yes | Metro network |
| MTC Bus | Yes | Yes | Yes | Supported routes/corridors |

The user provides an origin, destination, bike mileage, and optimization preference. The backend calculates the available transportation options and produces a comparison.

**General workflow:**

```
User Input
    |
    v
Origin + Destination
    |
    v
Routing and Transit Data
    |
    +------------------+
    |                  |
    v                  v
  Bike            Metro / Bus
    |                  |
    +--------+---------+
             |
             v
     Calculate Metrics
             |
     +-------+-------+
     |       |       |
     v       v       v
   Time    Cost     CO2
     |       |       |
     +-------+-------+
             |
             v
   Recommendation Engine
             |
             v
      Score and Rank
             |
             v
       Best Commute
```

---

## Features

### 1. Multi-Modal Transportation Comparison

The application compares different transportation options for the same journey. For each available mode, the system attempts to provide estimated travel time, estimated cost, estimated CO2 emissions, an overall score, and a recommendation status. This allows the user to compare options directly rather than evaluating each one independently.

### 2. Bike Cost Calculation

The user provides their bike mileage (for example, 45 km/L). The application calculates fuel consumption and trip cost using:

```
Fuel Used = Distance / Mileage
Trip Cost = Fuel Used x Petrol Price
```

The petrol price is a configurable parameter (currently defaulted to Rs. 100.75 per litre) rather than one pulled from a live petrol-price API.

### 3. Chennai Metro Journey Planning

The Metro calculation accounts for the fact that the user's origin and destination are not necessarily Metro stations. For example, a trip from VIT Chennai to Tambaram is not treated as a direct station-to-station journey. Instead, the journey is broken into three parts:

```
VIT Chennai
     |
     v
Access / Walking
     |
     v
Nearest or Suitable Metro Station
     |
     v
Metro Station A --- Chennai Metro --- Metro Station B
     |
     v
Last-Mile Journey
     |
     v
Tambaram
```

- **Access Leg** — Source to Metro boarding station (distance and time to reach the station).
- **Metro Leg** — Boarding station to exit station, including stations, route, line/interchange information, fare, and travel time.
- **Last-Mile Leg** — Exit station to final destination.

The Metro fare is calculated for the actual station-to-station journey rather than treating arbitrary locations as Metro stations.

### 4. MTC Bus Comparison

The application includes MTC Bus comparison for supported routes and corridors. Where sufficient route information is available, the system provides the bus service/route, boarding point, alighting point, estimated travel time, fare, and estimated CO2.

The project intentionally does not fabricate bus routes when reliable data is unavailable — unsupported routes are handled gracefully rather than producing misleading information. The current implementation is an MVP and does not attempt complete Chennai-wide dynamic MTC routing.

### 5. Estimated CO2 Calculation

The application estimates the environmental impact of each mode using documented emission factors and assumptions. These are presented as **estimated** CO2, not exact real-world measurements.

**Bike**

```
Bike CO2 = (Distance / Mileage) x Petrol CO2 Factor
```

Documented petrol emission factor: approximately 2.310 kg CO2/litre, with a default bike mileage of 45 km/L.

**Metro**

Estimated using passenger-kilometre electricity consumption and an electricity-grid emissions factor:

- Baseline: 0.050 kWh/passenger-km
- Grid factor: 0.716 kg CO2/kWh
- Resulting estimate: approximately 0.0358 kg CO2/passenger-km

**Bus**

Estimated using fuel type, bus fuel economy, passenger occupancy, and passenger journey distance. Documented baseline: approximately 0.0255 kg CO2/passenger-km.

Assumptions and sources are documented separately in the project's emission methodology documentation.

---

## Recommendation Engine

The central feature of Smart Commute Chennai is the recommendation engine. The application does not simply show three routes and leave the user to manually compare them — it calculates scores for the available options and ranks them according to the user's selected preference.

Supported preferences:

| Preference | Priority Order |
|---|---|
| Fastest | Time > Cost > Environmental Impact |
| Cheapest | Cost > Time > Environmental Impact |
| Greenest | Environmental Impact > Time > Cost |
| Best Overall | Balanced weighting across all factors (weights configurable in the recommendation logic) |

### Recommendation Explanation

The recommendation does not simply state "Metro is recommended." It explains why the option was selected, for example:

**Recommended: Metro**

Reason:
- Lower estimated CO2 than the bike option
- Competitive total journey cost
- Acceptable travel time
- Highest overall score for the selected preference

This makes the recommendation transparent and lets the user understand the reasoning behind the result.

---

## Methodology

Smart Commute Chennai treats transportation selection as a **multi-objective optimization problem**. For each mode, the system determines travel time, travel cost, and estimated CO2. These values are normalized and converted into scores, and the recommendation engine applies the user's selected preference on top of them.

**Conceptual process:**

```
Transportation Options
        |
        v
Calculate Metrics
        |
        v
Normalize Metrics
        |
        v
Calculate Scores
        |
        v
Apply User Preference
        |
        v
Rank Transportation Modes
        |
        v
Generate Recommendation
```

The purpose of this methodology is to avoid recommending a transportation mode based on a single metric.

### Routing Methodology

The project uses routing and transit-specific logic rather than applying the same calculation to every mode. Road-based journeys use routing data for distance, duration, and route information; transit journeys use their respective network data. This distinction matters most for Metro — a raw road distance between two points is never treated as a direct Metro journey. Instead:

```
User Location -> Suitable Metro Station -> Metro Network -> Suitable Exit Station -> Destination
```

This provides a more realistic representation of multimodal travel.

---

## APIs and External Services

| Service | Purpose | Why it was used |
|---|---|---|
| **OSRM** (Open Source Routing Machine) — `https://router.project-osrm.org/` | Road-based routing and distance/duration estimation for bike journeys; also supports access and last-mile calculations. | Free, open-source, and self-hostable routing engine that gives realistic road distances and durations without depending on a paid mapping API. Fallback logic exists for when the service is unavailable, treated as an estimation rather than an exact route. |
| **Chennai Metro structured data** | Station locations, lines, connections, interchanges, and fare information used to construct valid Metro journeys. | Ensures Metro journeys are calculated between real stations rather than arbitrary geographic points, and that fares reflect actual station-to-station data. |
| **MTC route and fare data** | Route and fare information for supported bus corridors. | Chennai does not have a comprehensive real-time public MTC API, so the project maintains verified data for supported corridors and reports unsupported routes rather than fabricating them. |

No live petrol-price API is used; petrol price is a configurable parameter to keep the cost calculation predictable and independent of external rate limits.

---

## Data Sources and Provenance

The project documents where its transportation and environmental data comes from. The repository includes:

- `DATA_AVAILABILITY_REPORT.md`
- `DATA_PROVENANCE.md`
- `REVISED_DATA_AVAILABILITY_REPORT.md`
- `EMISSION_METHODOLOGY.md`

These documents describe data sources, availability, provenance, emission assumptions, fare assumptions, known limitations, and confidence/coverage. The project intentionally distinguishes between verified data and estimated values.

---

## Technology Stack

**Frontend** — `frontend/`
- React
- TypeScript
- Vite
- React DOM
- React Leaflet
- Leaflet
- Lucide React

**Backend** — `backend/`
- Python
- FastAPI
- Pydantic
- SQLAlchemy

The backend is organized into separate services for transportation calculations and recommendation logic:

```
backend/
    |
    +-- API
    +-- Core
    +-- Data
    +-- Models
    +-- Schemas
    +-- Services
          |
          +-- Routing
          +-- Bike
          +-- Metro
          +-- Bus
          +-- Recommendation
```

**Database**

The current MVP uses SQLite for local application data, storing transit-related information required by the backend. The architecture keeps structured transit data separate from calculation logic.

---

## How the Website Works

1. User opens Smart Commute Chennai
2. Enters origin
3. Enters destination
4. Enters bike mileage
5. Selects optimization preference
6. Clicks "Compare Commute Options"
7. Frontend sends request to FastAPI backend
8. Backend determines available transportation options
9. Routing/transit services calculate journey information
10. Cost engine calculates transportation cost
11. CO2 engine estimates environmental impact
12. Recommendation engine scores the options
13. Options are ranked
14. Frontend displays comparison
15. User sees the recommended transportation option

---

## Example Journey

**Origin:** VIT Chennai
**Destination:** Chennai Central
**Preference:** Best Overall
**Bike Mileage:** 45 km/L

The system calculates:

- **Bike** — road distance, travel time, fuel consumption, cost, estimated CO2
- **Metro** — access to suitable station, Metro journey, last-mile journey, total time, total cost, estimated CO2
- **Bus** — supported route, boarding/alighting information, estimated time, fare, estimated CO2

The recommendation engine then compares the resulting options.

---

## Project Architecture

```
                         USER
                           |
                           v
                    React Frontend
                           |
                           | HTTP API
                           v
                      FastAPI Backend
                           |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
   Routing Service    Transit Services    Data Services
        |                  |                  |
        v                  v                  v
      OSRM              Metro                MTC
                        Network              Data
        |
        v
   Bike Routing

        +------------------+------------------+
                           |
                           v
                     Cost Engine
                           |
                           v
                     CO2 Engine
                           |
                           v
                Recommendation Engine
                           |
                           v
                    Score + Rank
                           |
                           v
                    Final Results
                           |
                           v
                    React Frontend
```

---

## Local Development

### Clone the Repository

```bash
git clone https://github.com/Rajsaura/NEXUS_Movability__app.git
cd NEXUS_Movability__app
```

### Backend

```bash
cd backend
```

Create a virtual environment:

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS**
```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI application using the project's configured entry point. The backend also provides a health endpoint:

```
GET /api/health
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

For a production build:

```bash
npm run build
```

---

## Testing

The project contains backend and integration testing infrastructure. Tests verify:

- Backend health
- API responses
- Commute comparison
- Bike calculations
- Metro calculations
- Bus calculations
- Recommendation ranking
- Cost calculations
- CO2 calculations
- Data availability
- Error handling

Backend tests live under `backend/tests/`. The project also contains `integration_test.py`.

---

## Current Limitations

Smart Commute Chennai is currently an MVP and should not be considered a complete real-time Chennai transportation platform. Current limitations include:

- MTC Bus coverage is limited to supported corridors; complete Chennai-wide dynamic MTC routing is not currently implemented.
- Metro delays are not currently predicted.
- Real-time crowding information is not currently available.
- Real-time traffic integration is limited.
- OSRM depends on external service availability and rate limits.
- Emissions are estimates based on documented assumptions.
- Petrol price is configurable rather than obtained from a live fuel-price API.
- Transit information can be expanded as more verified data becomes available.
- The application does not currently provide full real-time multimodal optimization across every possible transport combination.

The project deliberately prefers transparent limitations over fabricated transportation results.

---

## Data Transparency

A core principle of the project: **do not present estimated information as exact information.**

For example, "Estimated CO2" is intentionally different from claiming "Exact CO2 produced." Similarly, if a complete bus route cannot be established from available data, the application identifies the limitation instead of inventing a route. This matters because transportation recommendations can influence real-world decisions.

---

## Development Philosophy

1. **Do Not Fabricate Transportation Data** — If reliable information is unavailable, the application communicates that limitation instead of generating a fake result.
2. **Make Assumptions Explicit** — Fare calculations, emission calculations, and fallback routing estimates are documented.
3. **Optimize for Decisions, Not Just Routes** — The objective is not "here is your route," but "here are the available options, here is how they compare, here is which option best matches your priority, and here is why."

This project was developed using a vibe-coding and AI-assisted development workflow, with AI tools used for exploring implementation approaches, generating initial code, building frontend components and backend services, debugging, investigating errors, iterating on logic, and improving documentation. The process was iterative, not "generate once and accept without review":

```
Idea -> AI-assisted implementation -> Run application -> Identify problems
     -> Debug -> Test -> Review -> Iterate
```

The project also serves as an experiment in building a practical civic-tech application through AI-assisted development while maintaining explicit data assumptions, methodology, and limitations.

---

## Future Plans

1. **Full Chennai MTC Network** — Complete route coverage, more bus stops, better boarding/alighting detection, transfer-aware routing, improved fare calculation, and better service availability information.
2. **Advanced Multimodal Routing** — Expand from individual transport modes into complete multimodal journeys (e.g., Walk -> Bus -> Metro -> Walk, or Bike -> Metro -> Walk) toward a proper multimodal journey planner.
3. **Real-Time Traffic** — Integrate live traffic information to improve bike travel-time estimates, road access times, last-mile estimates, and dynamic recommendations.
4. **Real-Time Transit Information** — Live bus locations, bus arrival estimates, Metro service disruptions and delays, and transit service availability.
5. **Crowd and Comfort Factors** — Consider crowding, number of transfers, walking distance, accessibility, weather, comfort, and reliability so similar routes can be differentiated by convenience.
6. **Personalized Recommendations** — Allow users to define detailed preferences, e.g. "I am willing to spend Rs. 20 more to save 15 minutes," or "I prefer public transportation."
7. **Historical Commute Analytics** — Track weekly transportation costs, estimated CO2 impact, time spent travelling, most-used modes, money saved, and emissions avoided.
8. **Weather-Aware Recommendations** — Adjust preference weighting under conditions such as heavy rain (e.g., reduce preference for two-wheelers, prioritize Metro/Bus).
9. **Expand Beyond Chennai** — Extend the architecture to other Indian cities such as Bengaluru, Hyderabad, Mumbai, Delhi, Pune, and Kolkata, evolving into a multi-city mobility platform.

---

## Vision

The long-term vision of Smart Commute Chennai is to evolve from a transportation comparison application into a broader mobility decision platform. Instead of asking "How do I get there?", the system should eventually answer:

> "What is the best way for me to get there right now, considering time, money, environmental impact, convenience, and the available transportation network?"

The project combines mobility, data, sustainability, routing, decision support, and AI-assisted development to create a practical transportation tool for urban commuters.

---

## Project Status

**Status:** MVP / Hackathon Prototype

The current version demonstrates the core concept of comparing transportation modes and generating a recommendation based on measurable factors and user preferences. The system is actively evolving, with future work focused on improving transit coverage, multimodal routing, real-time information, and personalization.

---

## Contributing

Suggestions, bug reports, and improvements are welcome. If you find an issue with the application or have an idea for improving the transportation model, open an issue or submit a pull request. When contributing transportation data, please provide the source and methodology whenever possible.

---

## License

See the repository's license information for the applicable terms.

---

## Author

**Rajsaura**

Smart Commute Chennai was developed as an exploration of urban mobility, data analytics, sustainability, transportation optimization, and AI-assisted development.

If you find the project interesting, consider starring the repository and following its development.
