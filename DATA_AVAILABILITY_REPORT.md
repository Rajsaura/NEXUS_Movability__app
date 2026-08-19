# Smart Commute Chennai - Data Availability Report

## Executive Summary
This report presents the research and validation findings for data sources required by **Smart Commute Chennai**. The assessment covers Chennai Metro (CMRL), Metropolitan Transport Corporation (MTC) Bus, CUMTA Open Data, road routing engines, fuel pricing, and carbon emission factors.

---

## 1. Source Breakdown & Investigation

### A. CUMTA Open Data (`https://opendata.cumta.org/`)
- **Status**: Host unreachable / domain currently inactive (`opendata.cumta.org`).
- **Research Findings**: Official CUMTA open GTFS datasets are not publicly accessible via an active API endpoint. Community repositories (e.g. `ChennaiGTFS`) exist but contain static and unverified geometric representations.
- **Decision**: Rely on verified static official CMRL data and MTC corridor datasets rather than unmaintained community GTFS mirrors.

### B. Official Chennai Metro Rail Limited (CMRL) (`https://chennaimetrorail.org/`)
- **Data Available**: Complete station list (Blue Line: Wimco Nagar Depot - Airport; Green Line: Chennai Central - St. Thomas Mount), interchange point (Alandur), station-to-station fare matrix (₹10 - ₹50), line distances, and travel durations.
- **Format**: Official published fare charts and station schedules.
- **Access Method**: Pre-validated static database seed (`metro_stations`, `metro_connections`, `metro_fares`).
- **Confidence**: **HIGH** (Official published fare and network structure).

### C. Official MTC Bus (`https://mtcbus.tn.gov.in/`)
- **Data Available**: Official fare stage structure (2018 revision, starting at ₹5 up to ₹23 for ordinary services; express and deluxe fare tiers), route-to-stage mappings.
- **Format**: Official published stage lists and fare rules.
- **Access Method**: Structured static dataset covering key demonstration corridors (e.g. VIT Chennai – Tambaram – Guindy – Central, Airport – Guindy – Central).
- **Limitations**: Full city-wide dynamic multi-transfer bus routing lacks official open API. City-wide unsupported routes transparently display *"Bus comparison available for supported corridors in MVP"*.
- **Confidence**: **MEDIUM** (Exact for supported demonstration corridors; transparent fallback for unsupported routes).

### D. Routing & Geocoding Provider
- **Provider**: OpenStreetMap (OSRM for road distance/duration/geometry + Nominatim for location geocoding), abstracted behind a pluggable `RoutingProvider` interface (supporting fallback/override via Google Maps or Mapbox if `ROUTING_API_KEY` is provided).
- **Format**: REST JSON APIs.
- **Confidence**: **HIGH** (Real road distances and durations for Chennai road network).

### E. Petrol Price & Carbon Emission Factors
- **Petrol Price**: Configurable environment variable `PETROL_PRICE_PER_LITRE` (Default: ₹100.75 / Litre).
- **Emission Factors**:
  - Private Bike: `0.12 kg CO2 / km` (based on average 120-150cc commuter motorcycle emission standards).
  - Chennai Metro: `0.015 kg CO2 / passenger-km` (based on grid electricity emission factor and average metro occupancy).
  - MTC Bus: `0.035 kg CO2 / passenger-km` (based on diesel bus emissions divided by average commuter load factor).
- **Confidence**: **MEDIUM** (Clearly labeled as *Estimated CO2* with documented assumptions).

---

## 2. Data Availability Matrix

| Requirement | Data Source | Available? | Implementation Method | Confidence |
|-------------|-------------|------------|-----------------------|------------|
| **Bike Distance** | OpenStreetMap OSRM API | Yes | Direct API lookup | HIGH |
| **Bike ETA** | OpenStreetMap OSRM API | Yes | Direct API lookup | HIGH |
| **Metro Stations** | CMRL Official / Verified Dataset | Yes | Static DB (`metro_stations` table) | HIGH |
| **Metro Route** | CMRL Network Graph (Blue & Green lines + Alandur) | Yes | NetworkX Dijkstra pathfinding | HIGH |
| **Metro Fare** | CMRL Official Published Fare Matrix | Yes | Station-to-station matrix lookup (`metro_fares` table) | HIGH |
| **Metro Time** | CMRL Schedules + Access/Egress candidate routing | Yes | Network graph time + OSRM access/egress | HIGH |
| **Bus Stops** | MTC Official Route & Stage Data | Yes (Corridor) | Pre-validated corridor dataset (`bus_stops` table) | MEDIUM |
| **Bus Routes** | MTC Official Route Mappings | Yes (Corridor) | Direct route path lookup (`bus_routes` table) | MEDIUM |
| **Bus Timetable** | MTC Schedule Averages | Partial | Frequency-based average travel time calculation | MEDIUM |
| **Bus Fare** | MTC Official Stage Fare Rule (2018 Revision) | Yes | Stage count fare rule calculation (`fare_rules` table) | HIGH (for supported routes) |
| **Petrol Price** | Local TN Config | Yes | Configurable variable (`PETROL_PRICE_PER_LITRE`) | MEDIUM |
| **CO2 Factors** | Documented Mobility Emission Standards | Yes | Configurable emission factors structure | MEDIUM |

---

## 3. Final Implementation Decision

| Feature | Decision | Implementation Details |
|---------|----------|------------------------|
| **Bike Mode** | **IMPLEMENT WITH REAL DATA** | OSRM road API for route distance & duration; configurable petrol price; user-editable mileage (default 45 km/L); emission factor calculation. |
| **Metro Mode** | **IMPLEMENT WITH OFFICIAL STATIC DATA** | Graph model of CMRL network; candidates search for nearest source & destination stations; access/egress walking routing; official station-to-station fare matrix. |
| **MTC Bus Mode** | **IMPLEMENT WITH OFFICIAL STATIC DATA (CORRIDOR SCOPE)** | Supported demonstration corridors with official stage-wise fares; transparent status message when route is unsupported; modular design so additional routes can be appended. |
| **Recommendation Engine** | **IMPLEMENT WITH CALCULATED ESTIMATE** | Deterministic score normalization across Time, Cost, CO2, and Convenience; user preference weighting (Fastest, Cheapest, Greenest, Best Overall); deterministic "Why Recommended" explanation generator. |
