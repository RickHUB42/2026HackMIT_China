import os
import base64
import ast

from openai import OpenAI

client = OpenAI(
    api_key="sk-JWSXYvXu3w5dGphYLtruCBRA53HYzLsjgC4bXcq5yQyjyzsJ",
    base_url="https://api.moonshot.cn/v1",
)


def find_food(img_path: str) -> dict[str, str]:
    with open(img_path, "rb") as f:
        image_data = f.read()

    ext = os.path.splitext(img_path)[1].lstrip(".").lower()
    mime = "jpeg" if ext == "jpg" else ext
    image_url = f"data:image/{mime};base64,{base64.b64encode(image_data).decode('utf-8')}"

    prompt = """
    List all the types of food you see and their quantities
    You may think before you speak

    Your final line of output must be a python dict where the keys are the food types and the values are the quantities in kg, you can estimate the quantities during your CoT. It must be ONE LINE, that is no '\n'.
    The last line must be directly parse-able by eval

    For example
    [Your CoT ...]
    [Your CoT ...]
    [Your CoT ...]
    [Your CoT ...]
    {'a': 2, 'b': 3}

    Wrong example
    [Your CoT ...]
    [Your CoT ...]
    [Your CoT ...]
    [Your CoT ...]
    {
        'a': 2,
        'b': 3,
    }
    """

    completion = client.chat.completions.create(
        model="kimi-k2.5",
        messages=[
            {
                "role": "system",
                "content": "You are the most advanced food recognition system",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            },
        ],
    )

    res = completion.choices[0].message.content
    if res is None:
        raise Exception("The visionLLM is striking")

    print(res)

    food_dct = ast.literal_eval(res.strip().split("\n")[-1])
    assert isinstance(food_dct, dict)
    assert all(
        [
            isinstance(k, str) and (isinstance(v, int) or isinstance(v, float))
            for k, v in food_dct.items()
        ]
    )

    return food_dct


if __name__ == "__main__":
    print(find_food("./data/sample_fridge.jpg"))
