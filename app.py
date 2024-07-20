import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from finder import get_ingredients, get_recipe, get_recipe_instructions

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in [
        "png",
        "jpg",
        "jpeg",
    ]


@app.route("/")
def index():
    return render_template("index.html", text="Upload a file to find recipes")


@app.route("/get-ingredients", methods=["POST"])
def upload_source():
    if request.method == "POST":
        # check if the post request has the file part
        f = request.files["file"]
        if f.filename == "":
            print("No file Name")
            return redirect(request.url)
        if not allowed_file(f.filename):
            print("File extension not allowed!")
            return redirect(request.url)
        else:
            # full_filename = secure_filename(f.filename)

            ingredients = get_ingredients(f)
            print(ingredients)
            return render_template("index.html", ingredients=ingredients, recipes=None)


@app.route("/get-recipes", methods=["POST"])
def get_recipes():
    if request.method == "POST":
        recipe_list = []
        ingredients = request.form["ingredients"].split(",")
        number = int(request.form["number"])
        recipes = get_recipe(ingredients, number)
        if recipes["code"] == 402:
            return render_template(
                "index.html",
                text="You have exceeded the number of requests. Please try again later.",
            )
        for x in recipes:

            response = get_recipe_instructions(x["id"])
            recipe_credit = response["sourceUrl"]
            recipe_overview = response["spoonacularSourceUrl"]
            missed = [ingred["name"] for ingred in x["missedIngredients"]]
            recipe_list.append(
                [
                    x["title"],
                    x["image"],
                    missed,
                    recipe_credit,
                    recipe_overview,
                ]
            )
        return render_template(
            "index.html", ingredients=ingredients, recipes=recipe_list
        )


@app.route("/get-instructions", methods=["POST"])
def get_instructions():
    if request.method == "POST":
        id = request.form["id"]
        get_recipe_instructions(id)
        return render_template("index.html", text="Check console for instructions")


@app.route("/add-ingredient", methods=["POST"])
def add_ingredient():
    if request.method == "POST":
        ingredient = request.form["ingredient"]
        ingredients = request.form["ingredients"]
        ingredients += "," + ingredient
        ingredients = list(filter(None, ingredients.replace(" ", "").split(",")))

        print(ingredients)
        return render_template("index.html", ingredients=ingredients, recipes=None)


@app.route("/remove-ingredient", methods=["POST"])
def remove_ingredient():
    if request.method == "POST":
        ingredient = request.form["ingredient"]
        ingredients = request.form["ingredients"]
        ingredients = ingredients.replace(ingredient, "")
        ingredients = list(
            filter(None, ingredients.replace(" ", "").replace(",,", ",").split(","))
        )

        print(ingredients)
        return render_template("index.html", ingredients=ingredients, recipes=None)


app.run(debug=True)
