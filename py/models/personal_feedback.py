"""Personal feedback agent - evaluates meal nutrition + carbon via LLM."""
from openai import OpenAI

API_KEY = 'sk-e43c0370c3f64cdb8d403520e01b09cb'
SYSTEM_PROMPT = """You are a personalized nutrition reflection assistant. Evaluate meals through a "green lens" — both nutritional adequacy and environmental impact.

Input: nutrient delta values (positive=deficit, negative=surplus) and meal description.
Output: A SHORT emoji-rich response (max 3 sentences) with:
1. One key nutritional insight
2. One carbon footprint observation  
3. An overall emoji rating (🌱💚 = great, 🍃 = ok, 🔥 = high carbon)

Keep it casual, friendly, and brief. No headers or bullet points."""

def feedback(delta, meal):
    client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Nutrient deltas: {delta}\nMeal: {meal}"}
        ],
        temperature=0.7, stream=False, max_tokens=200
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    print(feedback('0,'*26, 'One hundred tons of beef'))
