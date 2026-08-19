import urllib.request, json

# Full integration test - via proxy (frontend port 3000 -> backend 8000)
payload = json.dumps({
    "origin": {"text": "VIT Chennai", "lat": 12.8406, "lng": 80.1534},
    "destination": {"text": "Chennai Central", "lat": 13.0827, "lng": 80.2757},
    "priority": "best_overall",
    "bike_mileage_kmpl": 45.0
}).encode()

req = urllib.request.Request(
    "http://localhost:3000/api/commute/compare",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)
r = urllib.request.urlopen(req)
data = json.loads(r.read())

rec = data["recommended_option"]
print("=== INTEGRATION TEST VIA VITE PROXY (port 3000 -> 8000) ===")
print("Status: 200 OK")
print("Recommended mode:", rec["mode"])
print("Score:", rec["overall_score"])
print("Time (min):", rec["total_time_minutes"])
print("Cost (INR):", rec["total_cost_inr"])
print("CO2 (kg):", rec["estimated_co2_kg"])
print("Why bullets:")
for b in rec["why_recommended"]:
    print("  -", b)
print()
print("All Options:")
for opt in data["options"]:
    s = "OK" if opt["is_supported"] else "UNSUPPORTED"
    print(f"  [{s}] {opt['mode']} | dist={opt['total_distance_km']}km | time={opt['total_time_minutes']}min | cost=INR{opt['total_cost_inr']}")

print()
print("Provenance for each supported mode:")
for opt in data["options"]:
    if opt["is_supported"]:
        p = opt["provenance"]
        print(f"  Mode={opt['mode']}")
        print(f"    distance.source_type : {p['distance']['source_type']}")
        print(f"    fare.source_type     : {p['fare']['source_type']}")
        print(f"    co2.source_type      : {p['co2']['source_type']}")
        print(f"    ui_co2_label         : {p.get('ui_co2_label', 'N/A')}")
print()
print("INTEGRATION TEST: PASSED")
