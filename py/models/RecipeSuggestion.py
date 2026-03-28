"""Bridge fridgeshit (fridge food detection) → RAG recipe suggestion."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'RAG'))
import ragstuff
from fridgeshit import find_food

def suggest(img_path, n_recipes=5):
    """
    1. Detect foods in fridge image via fridgeshit
    2. Query RAG for recipes matching those ingredients
    Returns: { foods: {name: kg}, recipes: [{ title, ingredients }] }
    """
    foods = find_food(img_path)
    query_str = ", ".join(foods.keys())
    idxs = ragstuff.query(query_str, n_results=n_recipes)
    recipes = []
    for idx in idxs:
        row = ragstuff.df.iloc[idx]
        recipes.append({"title": row["Title"], "ingredients": row["Ingredients"], "instructions": row["Instructions"]})
    return {"foods": foods, "recipes": recipes}

if __name__ == "__main__":
    import json
    p = sys.argv[1] if len(sys.argv) > 1 else "./data/sample_fridge.jpg"
    res = suggest(p)
    print(json.dumps(res, default=str))
