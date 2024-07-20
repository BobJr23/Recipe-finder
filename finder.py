import requests
from io import BytesIO
import base64
import os
from PIL import Image
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("API_KEY")
clarapi_key = os.getenv("CLARAPI_KEY")


def get_recipe(ingredients: list, number: int):

    response = requests.get(
        f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={",".join(ingredients)}&number={number}&apiKey="
        + api_key
    ).json()
    return response


def get_recipe_instructions(id: int):

    response = requests.get(
        f"https://api.spoonacular.com/recipes/{id}/information?apiKey="
        + api_key
    ).json()
    return response
    


def get_bytes(file):
    img = Image.open(file)
    imgByteArr = BytesIO()
    img.save(imgByteArr, format="PNG")
    imgByteArr = imgByteArr.getvalue()
    ret = base64.b64encode(imgByteArr).decode()
    return ret


def get_ingredients(file):
    read = get_bytes(file)
    ret = []
    response = requests.post(
        "https://api.clarifai.com/v2/users/clarifai/apps/main/models/food-item-v1-recognition/versions/dfebc169854e429086aceb8368662641/outputs",
        headers={
            "Authorization": "Key " + clarapi_key,
            "Content-Type": "application/json",
        },
        json={"inputs": [{"data": {"image": {"base64": read}}}]},
    ).json()
    
    
    for x in response["outputs"][0]["data"]["concepts"]:
        if x["value"] > 0.8:
            ret.append(x["name"])
    return ret


if __name__ == "__main__":
    ra = get_recipe(["apple", "banana", "orange", "peppers"], 5)
    print(ra)
    
    
