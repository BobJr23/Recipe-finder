from flask import Flask, request, redirect, url_for, render_template, make_response
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

@app.route("/set-api-key", methods=["POST"])
def set_api_key():
    if request.method == "POST":
        api_key = request.form["api_key"]
        clarapi_key = request.form["clarapi_key"]
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie("API_KEY", api_key)
        resp.set_cookie("CLARAPI_KEY", clarapi_key)
        return resp

@app.route("/get-ingredients", methods=["POST"])
def upload_source():
    if request.method == "POST":
        f = request.files["file"]
        if f.filename == "":
            print("No file Name")
            return redirect(request.url)
        if not allowed_file(f.filename):
            print("File extension not allowed!")
            return redirect(request.url)
        else:
            api_key = request.cookies.get("API_KEY")
            clarapi_key = request.cookies.get("CLARAPI_KEY")
            ingredients = get_ingredients(f, clarapi_key)
            print(ingredients)
            return render_template("index.html", ingredients=ingredients, recipes=None)


@app.route("/get-recipes", methods=["POST"])
def get_recipes():
    if request.method == "POST":
        recipe_list = []
        ingredients = request.form["ingredients"].split(",")
        number = int(request.form["number"])
        api_key = request.cookies.get("API_KEY")
        recipes = get_recipe(ingredients, number, api_key)
        for x in recipes:
            response = get_recipe_instructions(x["id"], api_key)
            recipe_credit = response["sourceUrl"]
            recipe_overview = response["spoonacularSourceUrl"]
            missed = [ingred["name"] for ingred in x["missedIngredients"]]
            recipe_list.append([x["title"], x["image"], missed, recipe_credit, recipe_overview])
        return render_template("index.html", ingredients=ingredients, recipes=recipe_list)



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
