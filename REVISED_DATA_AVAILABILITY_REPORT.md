# Revised Data Availability & Provenance Report (Corrected)

**Project**: Smart Commute Chennai  
**Date of Audit**: 2026-08-19  
**Status**: Comprehensive Data Verification & Provenance Corrections Applied  

---

## 1. CUMTA Audit & Domain Status

- **Primary URL Tested**: `https://opendata.cumta.org/`
- **Audit Timestamp**: 2026-08-19 10:14:12 IST
- **Result**: Host unreachable (`dial tcp: lookup opendata.cumta.org: no such host`).
- **Official Government Portal**: `https://cumta.tn.gov.in/` (Active, `200 OK`)
- **Finding**: Search confirms **no public open GTFS feed API endpoint is published on cumta.tn.gov.in**.
- **Conclusion**: CUMTA open GTFS feeds are **UNAVAILABLE** for dynamic public consumption.

---

## 2. Metro Data Verification & Rule Corrections

| Sub-Component | Provenance Type | Source & Verification Method | Production Suitability |
|---|---|---|---|
| **Station List** | `VERIFIED_STATIC` | Official CMRL Network Map (23 Blue Line + 17 Green Line stations). | Direct DB Import |
| **Lines Structure** | `VERIFIED_STATIC` | Official Blue Line & Green Line layout. | Direct DB Import |
| **Interchanges** | `VERIFIED_STATIC` | Official CMRL topology: Alandur & Chennai Central. | Direct DB Import |
| **Station Connections** | `VERIFIED_STATIC` | Physical adjacent track hops. | Direct DB Import |
| **Station Fares** | `CALCULATED_FROM_OFFICIAL_RULES` | **Calculated fare matrix derived from official CMRL fare rules, with validation against official examples** (distance slabs ₹10–₹50). Spot-checked against CMRL travel planner. | Direct DB Import |
| **Edge Weights** | `VERIFIED_STATIC` | **Primary weight is travel_time_minutes** (~2 min run time + 30s dwell; 5 min transfer penalty at Alandur). **OSRM road distance is strictly PROHIBITED between metro stations.** | Direct DB Import |

---

## 3. MTC Bus Verification & Fallback Rule

### Corridor Validation Example

```
Origin Stop: VIT Chennai (Vandalur-Kelambakkam Road)
Destination Stop: Chennai Central
Bus Route: 70G / 21G Corridor (Vandalur → Tambaram → Guindy → Central)
Official Route/Stage Source: MTC Official Stagewise Information (https://mtcbus.tn.gov.in/Home/stagewiseinfo)

Boarding Stage: Stage 1 (Vandalur Zoo / VIT Access)
Alighting Stage: Stage 14 (Chennai Central)
Stage Difference: 13 Stages (Approx. 28 km)
Service Category: Ordinary (White Board)

Calculated Fare: ₹23.00
Provenance Type: CALCULATED_FROM_OFFICIAL_RULES
Confidence Level: MEDIUM
```

### Bus Implementation Rule (`UNSUPPORTED_IN_MVP`)
Arbitrary city-wide bus routing is **NOT** implemented. A bus option is returned ONLY when all of the following are available:
1. Verified supported route
2. Verified boarding stage
3. Verified alighting stage
4. Verified service category
5. Valid fare rule

Otherwise, the system returns:
```json
{
  "status": "UNSUPPORTED_IN_MVP",
  "message": "Bus comparison is currently available only for supported Chennai corridors."
}
```

---

## 4. Petrol Price Parameter Rule

- **Parameter Name**: `PETROL_PRICE_PER_LITRE` (Default: ₹100.75 / L)
- **Classification**: **Configurable Application Parameter**
- **Frontend Label**: **"Petrol price used for estimate"** (Editable by user in settings).
- **Rule**: It is **NOT** described as a live/current real-world API feed.

---

## 5. OSRM & DistanceEstimateProvider Fallback Strategy

| Component | Function & Strategy |
|---|---|
| **Primary Provider** | `OSRMProvider` (`https://router.project-osrm.org/`) for Bike road routing and User Access/Egress walking routing. |
| **Fallback Component** | **`DistanceEstimateProvider`** (Haversine straight-line distance calculation with optional 1.3 road detour multiplier). |
| **Fallback Rules** | If OSRM is unavailable: <br> 1. Do **NOT** claim to return a real road route. <br> 2. Do **NOT** return fake route geometry (returns `geometry: null`). <br> 3. Mark distance `source_type`: `ESTIMATED_WITH_ASSUMPTIONS`, `confidence`: `LOW`. <br> 4. Mark ETA as estimated or unavailable. |

---

## 6. Revised Data Availability & Provenance Matrix

| Metric / Feature | Source | Provenance Type | Confidence | Exact Method | Limitation |
|---|---|---|---|---|---|
| **Bike Distance** | OSRM API | `LIVE_ROUTING` | `HIGH` | OSRM driving route lookup | Public API rate limits (Fallback: `DistanceEstimateProvider`) |
| **Bike Duration** | OSRM API | `LIVE_ROUTING` | `HIGH` | OSRM driving duration lookup | Standard road traffic profile |
| **Metro Stations** | CMRL Portal | `VERIFIED_STATIC` | `HIGH` | Seeded station coordinates & lines | Phase 1 operational network |
| **Metro Route** | CMRL Topology | `VERIFIED_STATIC` | `HIGH` | NetworkX pathfinding on travel time | Dynamic delay info unavailable |
| **Metro Fare** | CMRL Fare Slabs | `CALCULATED_FROM_OFFICIAL_RULES` | `MEDIUM` | Fare matrix calculated from official distance slabs + spot-checks | Derived token fare |
| **Metro Emissions** | CEA / CMRL | `ESTIMATED_WITH_ASSUMPTIONS` | `MEDIUM` | $0.050\text{ kWh/p-km} \times 0.716\text{ kg CO}_2/\text{kWh}$ | Documented assumptions baseline |
| **Bus Route / Fare** | MTC Gazette | `CALCULATED_FROM_OFFICIAL_RULES` | `MEDIUM` | Stage difference calculation on supported corridors | Unsupported routes return `UNSUPPORTED_IN_MVP` |
| **Bus Emissions** | WRI / GHG Platform | `ESTIMATED_WITH_ASSUMPTIONS` | `MEDIUM` | $2.68\text{ kg CO}_2/\text{L} \div 3.5\text{ km/L} \div 30\text{ passengers}$ | Documented assumptions baseline |
| **Petrol Price** | Local Config | `CALCULATED_FROM_USER_INPUT` | `MEDIUM` | Configurable setting (Default ₹100.75/L) | User editable parameter |
