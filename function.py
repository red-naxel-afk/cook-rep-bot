import sqlite3
from random import choice


# поиск по ингридиентам
def ingredients_search(ing):
    ingredients = ing.lower().split(',')

    con = sqlite3.connect("recipes_db.db")
    cur = con.cursor()
    result = cur.execute("""SELECT id, ingredients FROM recipes""").fetchall()
    # print(result)
    con.close()

    identical_recipes_id = list()  # id рецептов с точно такими же ингредиентами
    similar_recipes_id = list()  # id рецептов с этими же ингредиентами, но там есть и другие ингредиенты

    for rec in result:  # отбор рецептов с нужными ингредиентами
        fl = True
        for i in ingredients:
            if i not in rec[1].lower():
                fl = False
                break
        if fl and len(ingredients) == len(rec[1].split(', ')):
            identical_recipes_id.append(rec[0])
        elif fl:
            similar_recipes_id.append(rec[0])

    # print(identical_recipes_id)
    # print(similar_recipes_id)
    return identical_recipes_id, similar_recipes_id


# поиск по тегам
def tags_search(t):
    tags = set()  # введённые теги
    for tag in t.lower().split(', '):
        tags.add(tag)

    con = sqlite3.connect("recipes_db.db")

    cur = con.cursor()
    result = cur.execute("""SELECT id, tags FROM recipes""").fetchall()
    con.close()

    tags_recipes_id = list()  # id рецептов с нужными тегами

    for rec in result:  # отбор рецептов с нужными тегами
        if set(rec[1].split(';')) & tags == tags:
            tags_recipes_id.append(rec[0])
    # print(tags_recipes_id)
    return tags_recipes_id


def random_recipes():
    con = sqlite3.connect("recipes_db.db")
    cur = con.cursor()

    result = cur.execute("""SELECT id FROM recipes""").fetchall()
    result = list(map(lambda x: x[0], result))

    con.close()

    return choice(result)


print(ingredients_search('яйцо, йцу'))  # чет не так
