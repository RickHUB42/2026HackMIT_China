"""
Food GHG Emissions Search Tool
Uses LLM to match food items to emissions data keys.
"""

import csv
from typing import Optional, List, Dict

from openai import OpenAI

client = OpenAI(
    api_key="sk-JWSXYvXu3w5dGphYLtruCBRA53HYzLsjgC4bXcq5yQyjyzsJ",
    base_url="https://api.moonshot.cn/v1",
)


class FoodEmissionsSearcher:
    def __init__(self, csv_path: str = "data/ghg-per-kg-poore.csv"):
        self.data: Dict[str, dict] = {}
        self.food_names: List[str] = []
        self._load_data(csv_path)

    def _load_data(self, csv_path: str):
        """Load the emissions data from CSV."""
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                food_name = row["Entity"].strip()
                emissions = float(row["Greenhouse gas emissions per kilogram"])
                self.data[food_name.lower()] = {
                    "name": food_name,
                    "emissions": emissions,
                    "unit": "kg CO2e / kg",
                }
                self.food_names.append(food_name.lower())

    def search(self, query: str) -> Optional[dict]:
        """
        Search for emissions data using LLM to match the query to a key.

        Args:
            query: The food item to search for

        Returns:
            Dictionary with match info or None
        """
        if not query or not query.strip():
            return None

        query = query.strip()

        # Build the prompt with available food names
        food_list = "\n".join([f"- {name}" for name in self.food_names])

        prompt = f"""Given the user's query for a food item, find the best match from the list below.

Available food items:
{food_list}

User query: "{query}"

Respond with ONLY the exact food item name from the list that best matches the query.
Do not include any explanation, just the matching food name."""

        completion = client.chat.completions.create(
            model="kimi-k2.5",
            messages=[
                {
                    "role": "system",
                    "content": "You are a food matching system. Respond only with exact matches from the provided list.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        match = completion.choices[0].message.content.strip()

        if match == "NONE" or match not in self.data:
            return None

        result = self.data[match.lower()]
        return {
            "match": result["name"],
            "emissions": result["emissions"],
            "unit": result["unit"],
        }

    def get_emissions(self, query: str) -> Optional[float]:
        """
        Simple API to just get the emissions value.

        Args:
            query: The food item to search for

        Returns:
            Emissions value in kg CO2e / kg, or None if not found
        """
        result = self.search(query)
        return result["emissions"] if result else None

    def list_foods(self) -> List[str]:
        """Return all available food names."""
        return self.food_names.copy()


# Convenience function for simple usage
def get_food_emissions(
    food_name: str, csv_path: str = "data/ghg-per-kg-poore.csv"
) -> Optional[float]:
    """
    Get GHG emissions per kg for a food item.

    Args:
        food_name: Name of the food (e.g., "beef", "chicken", "apples")
        csv_path: Path to the CSV file

    Returns:
        Emissions in kg CO2e per kg of food, or None if not found
    """
    searcher = FoodEmissionsSearcher(csv_path)
    return searcher.get_emissions(food_name)


if __name__ == "__main__":
    # Demo usage
    searcher = FoodEmissionsSearcher()

    test_queries = [
        "beef",
        "chicken",
        "steak",
        "burger",
        "cow meat",
        "chocolate",
        "wine",
        "oats",
        "pork",
        "shrimp",
        "lamb",
        "mutton",
        "peanuts",
        "coffee",
        "bread",
        "tofu",
        "banana",
        "apples",
        "farm-raised fish",
        "dairy cow",
        "whole wheat",
    ]

    print("Food GHG Emissions Search Demo")
    print("=" * 60)

    for query in test_queries:
        result = searcher.search(query)
        if result:
            print(f"\n'{query}' -> {result['match']}")
            print(f"  Emissions: {result['emissions']} kg CO2e/kg")
        else:
            print(f"\n'{query}' -> No match found")
