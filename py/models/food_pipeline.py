"""
Bridge between foodstuff (mass estimation) and food_emissions_search (carbon lookup)
+ geographical_punishment (transport penalty).
"""

import os, sys, json
from foodstuff import work
from food_emissions_search import FoodEmissionsSearcher

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Geo'))
from geographical_punishment import emissions as geo_emissions


def analyze(img_path, cached_foodlist=None, user_lat=None, user_lon=None):
    m_dct = work(img_path, cached_foodlist=cached_foodlist)
    searcher = FoodEmissionsSearcher()
    use_geo = user_lat is not None and user_lon is not None

    results = []
    for food, mass_kg in m_dct.items():
        entry = {
            "food": food, "mass_kg": mass_kg,
            "emissions_per_kg": None, "matched_as": None, "geo_emissions": None,
        }
        match = searcher.search(food)
        if match:
            entry["matched_as"] = match["match"]
            entry["emissions_per_kg"] = match["emissions"]
        if use_geo and mass_kg > 0:
            try:
                entry["geo_emissions"] = geo_emissions(user_lat, user_lon, food, mass_kg)
            except Exception as e:
                print(f"[geo] Failed for {food}: {e}", file=sys.stderr)
        results.append(entry)
    return results


if __name__ == "__main__":
    img_path = sys.argv[1] if len(sys.argv) > 1 else "C:\\Users\\35668\\Documents\\SHSID\\HackMIT\\Web\\uploads\\3b3ab4852befeda595c56bc19b361d38.jpg"
    lat = float(sys.argv[2]) if len(sys.argv) > 2 else 31.2304
    lon = float(sys.argv[3]) if len(sys.argv) > 3 else 121.4737
    as_json = '--json' in sys.argv

    results = analyze(img_path, user_lat=lat, user_lon=lon)

    if as_json:
        print(json.dumps(results, default=str))
    else:
        print(f"\n{'Food':<25} {'Mass(kg)':<10} {'Matched As':<22} {'CO2e/kg':<10} {'Geo CO2e':<10}")
        print("=" * 80)
        for r in results:
            em = f"{r['emissions_per_kg']:.2f}" if r["emissions_per_kg"] else "N/A"
            geo = f"{r['geo_emissions']:.4f}" if r["geo_emissions"] else "N/A"
            matched = r["matched_as"] or "N/A"
            print(f"{r['food']:<25} {r['mass_kg']:<10.4f} {matched:<22} {em:<10} {geo:<10}")
