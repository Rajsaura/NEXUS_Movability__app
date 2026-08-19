# Transport Emission Methodology & Documented Assumptions Baseline

This document details the mathematical calculations, underlying domain assumptions, primary publications, and provenance for carbon emission factors used in **Smart Commute Chennai**.

All emission factors are classified as **`ESTIMATED_WITH_ASSUMPTIONS`** with confidence level **`MEDIUM`**.

The user interface explicitly labels all carbon metrics:  
**"Estimated CO2 based on documented assumptions."**

---

## 1. Transport Mode Emission Factor Calculations

### A. Private Motorcycle / Scooter (Bike)

- **Factor Provenance Type**: `CALCULATED_FROM_USER_INPUT` / `ESTIMATED_WITH_ASSUMPTIONS`
- **Confidence Level**: `MEDIUM`
- **Unit**: `kg CO2 / km`
- **Source Publication**: 
  - *2006 IPCC Guidelines for National Greenhouse Gas Inventories* (Volume 2: Energy, Chapter 3: Mobile Combustion)
  - IPCC Gasoline Carbon Factor: **2.310 kg CO2 per Litre of Petrol**
- **Calculation Formula**:
  $$\text{Bike CO}_2\text{ (kg)} = \frac{\text{Distance (km)}}{\text{Mileage (km/L)}} \times 2.310\text{ kg CO}_2\text{/L}$$
- **Default Baseline (at 45 km/L)**:
  $$\text{Default Factor} = \frac{2.310}{45.0} = 0.05133\text{ kg CO}_2\text{/km}$$
- **Scope**: Tailpipe combustion emissions per single rider.

---

### B. Chennai Metro (CMRL)

- **Factor Provenance Type**: `ESTIMATED_WITH_ASSUMPTIONS`
- **Confidence Level**: `MEDIUM`
- **Unit**: `kg CO2 / passenger-km`
- **Source Publications**:
  - *Central Electricity Authority (CEA), Ministry of Power, Govt of India: CO2 Baseline Database for the Indian Power Sector (v19, 2023-24)* — Grid Factor: **0.716 kg CO2 / kWh**.
  - *DMRC / CMRL Operational Sustainability Benchmarks* — Specific Energy Consumption (SEC): **0.050 kWh / passenger-km**.
- **Calculation Formula**:
  $$\text{Metro CO}_2\text{ per passenger-km} = 0.050\text{ kWh/p-km} \times 0.716\text{ kg CO}_2\text{/kWh} = 0.0358\text{ kg CO}_2\text{/passenger-km}$$
- **Documented Assumptions**:
  1. Specific Energy Consumption ($0.050\text{ kWh/p-km}$) assumes ~50% average operational train occupancy.
  2. Electricity grid baseline is derived from Southern Grid average power generation mix.

---

### C. MTC City Bus (Diesel)

- **Factor Provenance Type**: `ESTIMATED_WITH_ASSUMPTIONS`
- **Confidence Level**: `MEDIUM`
- **Unit**: `kg CO2 / passenger-km`
- **Source Publications**:
  - *India GHG Platform & WRI India Urban Transit Mobility Emission Benchmarks*
  - Commercial Diesel Carbon Factor: **2.680 kg CO2 / Litre**
- **Documented Numerical Inputs**:
  1. Average Heavy Commercial Bus Fuel Economy: **3.50 km / Litre**
  2. Average City Bus Passenger Occupancy: **30 passengers / bus**
- **Calculation Formula**:
  $$\text{Tailpipe CO}_2\text{ per bus-km} = \frac{2.680\text{ kg CO}_2\text{/L}}{3.50\text{ km/L}} = 0.7657\text{ kg CO}_2\text{/bus-km}$$
  $$\text{Bus CO}_2\text{ per passenger-km} = \frac{0.7657\text{ kg CO}_2\text{/bus-km}}{30\text{ passengers}} = 0.02552\text{ kg CO}_2\text{/passenger-km}$$
- **Documented Assumptions**:
  Assumes an average occupancy load factor of 30 passengers per vehicle across peak/off-peak operations.

---

## 2. Emission Factor Metadata Schema

```json
{
  "emission_factors": {
    "bike": {
      "mode": "BIKE",
      "source_type": "CALCULATED_FROM_USER_INPUT",
      "confidence": "MEDIUM",
      "petrol_co2_factor_kg_per_l": 2.310,
      "default_mileage_kmpl": 45.0,
      "default_factor_value": 0.0513,
      "unit": "kg_co2_per_km",
      "source_name": "2006 IPCC Guidelines for National Greenhouse Gas Inventories",
      "source_url": "https://www.ipcc-nggip.iges.or.in/public/2006gl/pdf/2_Volume2/V2_3_Ch3_Mobile_Combustion.pdf",
      "scope": "tailpipe_combustion",
      "ui_label": "Estimated CO2 based on documented assumptions"
    },
    "metro": {
      "mode": "METRO",
      "source_type": "ESTIMATED_WITH_ASSUMPTIONS",
      "confidence": "MEDIUM",
      "sec_kwh_per_pkm": 0.050,
      "grid_factor_kg_per_kwh": 0.716,
      "default_factor_value": 0.0358,
      "unit": "kg_co2_per_passenger_km",
      "source_name": "CEA CO2 Baseline Database v19 & DMRC/CMRL Operational Benchmarks",
      "source_url": "https://cea.nic.in/cdm-co2-baseline-database-for-the-indian-power-sector/",
      "scope": "operational_grid_scope2",
      "assumptions": ["SEC: 0.050 kWh/p-km", "Grid Factor: 0.716 kg CO2/kWh"],
      "ui_label": "Estimated CO2 based on documented assumptions"
    },
    "bus": {
      "mode": "MTC_BUS",
      "source_type": "ESTIMATED_WITH_ASSUMPTIONS",
      "confidence": "MEDIUM",
      "fuel_economy_kmpl": 3.50,
      "diesel_co2_factor_kg_per_l": 2.680,
      "average_occupancy": 30,
      "default_factor_value": 0.0255,
      "unit": "kg_co2_per_passenger_km",
      "source_name": "India GHG Platform & WRI India Urban Transit Benchmarks",
      "source_url": "http://www.ghgplatform-india.org/",
      "scope": "tailpipe_combustion_per_passenger",
      "assumptions": ["Fuel Economy: 3.50 km/L", "Average Occupancy: 30 passengers/bus"],
      "ui_label": "Estimated CO2 based on documented assumptions"
    }
  }
}
```

---

## 3. Mandatory UI Transparency Rule

Every CO2 display on the frontend MUST show:  
**"Estimated CO2 based on documented assumptions"**
