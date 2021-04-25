import sqlite3
from random import choice


# поиск по ингридиентам
def ingredients_search(ing):
    ingredients = ing.lower().split(';')

    con = sqlite3.connect("recipes_db.db")
    cur = con.cursor()
    result = cur.execute("""SELECT id, ingredients, name FROM recipes""").fetchall()

    # print(result)
    con.close()

    identical_recipes = list()  # id рецептов с точно такими же ингредиентами
    similar_recipes = list()  # id рецептов с этими же ингредиентами, но там есть и другие ингредиенты

    for rec in result:  # отбор рецептов с нужными ингредиентами
        ing_list = list(map(lambda x: x.lower(), rec[1].split(';')))
        ing_list.sort()

        ingredients.sort()

        if ing_list == ingredients:
            identical_recipes.append((rec[0], rec[2]))
        elif set(ing_list) & set(ingredients) != set():
            similar_recipes.append((rec[0], rec[2]))

    # print(identical_recipes)
    # print(similar_recipes)
    return identical_recipes, similar_recipes


# поиск по тегам
def tags_search(t):
    tags = list(map(lambda x: x.lower(), t.split(';')))  # введённые теги
    tags.sort()
    tags = set(tags)

    con = sqlite3.connect("recipes_db.db")

    cur = con.cursor()
    result = cur.execute("""SELECT id, tags, name FROM recipes""").fetchall()
    # print(result)
    con.close()

    identical_tags_recipes = list()
    similar_tags_recipes = list()

    for rec in result:  # отбор рецептов с нужными тегами
        tags_list = rec[1].split(';')
        tags_list.sort()

        tags_list = set(tags_list)

        if tags == tags_list:
            identical_tags_recipes.append((rec[0], rec[2]))
        elif tags_list & tags != set():
            similar_tags_recipes.append((rec[0], rec[2]))

    return identical_tags_recipes, similar_tags_recipes


def random_recipes():
    con = sqlite3.connect("recipes_db.db")
    cur = con.cursor()

    result = cur.execute("""SELECT id FROM recipes""").fetchall()
    result = list(map(lambda x: x[0], result))

    con.close()

    return choice(result)
