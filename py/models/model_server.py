"""Persistent Python model server - loads models once, serves via HTTP."""
import os, sys, json
from flask import Flask, request, jsonify

# Setup paths
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Geo'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'RAG'))

print("[model_server] Loading models...")
import visionllm
import yoloe
import depth2 as depth
import food_density_get
from food_emissions_search import FoodEmissionsSearcher
from geographical_punishment import emissions as geo_emissions
from fridgeshit import find_food as fridge_find_food
import ragstuff
from personal_feedback import feedback as pf_feedback
from foodstuffasync import work as foodstuff_work
from PIL import Image
import numpy as np

searcher = FoodEmissionsSearcher()
print("[model_server] All models loaded!")

app = Flask(__name__)


@app.route('/api/food_pipeline', methods=['POST'])
def food_pipeline():
    """Summary mode: image → mass estimation → emissions lookup."""
    data = request.json
    img_path = data['img_path']
    lat = float(data.get('lat', 31.2304))
    lon = float(data.get('lon', 121.4737))

    # Resize
    pil_img = Image.open(img_path)
    pil_img.thumbnail((500, 500), Image.Resampling.LANCZOS)
    resized = img_path + "_resized.jpg"
    pil_img.save(resized)

    m_dct = foodstuff_work(resized)
    use_geo = lat is not None and lon is not None

    results = []
    for food, mass_kg in m_dct.items():
        entry = {"food": food, "mass_kg": mass_kg,
                 "emissions_per_kg": None, "matched_as": None, "geo_emissions": None}
        match = searcher.search(food)
        if match:
            entry["matched_as"] = match["match"]
            entry["emissions_per_kg"] = match["emissions"]
        if use_geo and mass_kg > 0:
            try:
                entry["geo_emissions"] = geo_emissions(lat, lon, food, mass_kg)
            except Exception as e:
                print(f"[geo] Failed for {food}: {e}", file=sys.stderr)
        results.append(entry)
    return jsonify(results)


@app.route('/api/recipe_suggestion', methods=['POST'])
def recipe_suggestion():
    """Suggestion mode: fridge image → food detection → RAG recipes."""
    data = request.json
    img_path = data['img_path']
    n_recipes = data.get('n_recipes', 5)

    foods = fridge_find_food(img_path)
    query_str = ", ".join(foods.keys())
    idxs = ragstuff.query(query_str, n_results=n_recipes)
    recipes = []
    for idx in idxs:
        row = ragstuff.df.iloc[idx]
        recipes.append({"title": row["Title"], "ingredients": row["Ingredients"],
                        "instructions": row["Instructions"]})
    return jsonify({"foods": foods, "recipes": recipes})


@app.route('/api/personal_feedback', methods=['POST'])
def personal_feedback():
    """Personal feedback via LLM."""
    data = request.json
    result = pf_feedback(data['delta'], data['meal'])
    return jsonify({"feedback": result})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, threaded=True)
