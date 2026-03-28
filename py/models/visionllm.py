import os
import base64
import ast

from openai import OpenAI

client = OpenAI(
    api_key="sk-JWSXYvXu3w5dGphYLtruCBRA53HYzLsjgC4bXcq5yQyjyzsJ",
    base_url="https://api.moonshot.cn/v1",
)


def find_food(img_path: str, cot: bool = False) -> list[str]:
    with open(img_path, "rb") as f:
        image_data = f.read()

    image_url = f"data:image/{os.path.splitext(img_path)[1]};base64,{base64.b64encode(image_data).decode('utf-8')}"

    if cot:
        raise NotImplementedError()

    # backup
    """
    , and there should be clarification on its "unit" and "base quantity".
    If there are individual separated of that food type, the output should be "one [food name]" where "one" is the base quantity.
    Whereas, if the item of that type is clustered in a pile, it should just be "[food name]".

    """

    prompt = (
        "wtf"
        if cot
        else """
    List all the types of food you see in the image.
    Your output must only be all of them in a python list as strings.
    The names of the food should be singular.
    You need to be specific about the food. For example if there is pork, you should be specific about how it is cooked (is it roasted? is it barbequed?). You should also include a unit (the smallest unit possible). For example a banana (if the banana appears as a whole), or, if the banana is sliced into pieces, a piece of banana, or a slice of banana. Another common "unit" you might use would be "a", or example if you see some blue berries, you would use "a" blueberry, since a blueberry is the base unit of blue berries.

    Example output format
    ["a banana", "a slice of pizza"]

    An invalid example would be
    ["bananas", "pizza"
    because it doesn't have proper python syntax and "bananas" isn't singular
    """
    )

    completion = client.chat.completions.create(
        model="moonshot-v1-8k-vision-preview",
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

    food_lst = ast.literal_eval(res)
    assert isinstance(food_lst, list)
    assert all([isinstance(e, str) for e in food_lst])

    return food_lst


if __name__ == "__main__":
    print(find_food("./data/sample.png"))
