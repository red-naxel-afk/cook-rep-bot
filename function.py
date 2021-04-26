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


def daily_menu():
    con = sqlite3.connect("recipes_db.db")
    cur = con.cursor()
    result = cur.execute("""SELECT id, tags FROM recipes""").fetchall()
    con.close()

    menu = {}
    breakfast_drink = list()
    breakfast_meal = list()
    dinner_meal = list()
    afternoon_snack = list()
    supper_meal = list()
    supper_snack = list()
    supper_dessert = list()
    for i in result:
        if 'завтрак' in i[1].split(';') and 'напиток' in i[1].split(';'):
            breakfast_drink.append(i[0])
        if 'завтрак' in i[1].split(';') and 'напиток' not in i[1].split(';'):
            breakfast_meal.append(i[0])
        if 'обед' in i[1].split(';'):
            dinner_meal.append(i[0])
        if 'закуска' in i[1].split(';') and 'сладкое' not in i[1].split(';'):
            afternoon_snack.append(i[0])
        if 'ужин' in i[1].split(';'):
            supper_meal.append(i[0])
        if 'закуска' in i[1].split(';'):
            supper_snack.append(i[0])
        if 'десерт' in i[1].split(';'):
            supper_dessert.append(i[0])
    menu_list = [breakfast_drink, breakfast_meal, dinner_meal, afternoon_snack,
                 supper_meal, supper_snack, supper_dessert]
    menu_id = list()
    for i in menu_list:
        rnd = choice(i)
        while rnd in menu_list:
            rnd = choice(i)
        menu_id.append(rnd)
    return menu_id


def vegetarian_menu():
    con = sqlite3.connect("recipes_db.db")
    cur = con.cursor()
    result = cur.execute("""SELECT id, tags FROM recipes""").fetchall()
    con.close()

    menu = {}
    breakfast_drink = list()
    breakfast_meal = list()
    dinner_meal = list()
    afternoon_snack = list()
    supper_meal = list()
    supper_snack = list()
    for i in result:
        if 'завтрак' in i[1].split(';') and 'напиток' in i[1].split(';'):
            breakfast_drink.append(i[0])
        if 'завтрак' in i[1].split(';') and 'напиток' not in i[1].split(';') and 'мясо' not in i[1].split(';'):
            breakfast_meal.append(i[0])
        if 'обед' in i[1].split(';') and 'мясо' not in i[1].split(';'):
            dinner_meal.append(i[0])
        if 'закуска' in i[1].split(';') and 'сладкое' not in i[1].split(';') and 'мясо' not in i[1].split(';'):
            afternoon_snack.append(i[0])
        if 'ужин' in i[1].split(';') and 'мясо' not in i[1].split(';'):
            supper_meal.append(i[0])
        if 'закуска' in i[1].split(';') and 'мясо' not in i[1].split(';'):
            supper_snack.append(i[0])
    menu_list = [breakfast_drink, breakfast_meal, dinner_meal, afternoon_snack,
                 supper_meal, supper_snack]
    menu_id = list()
    for i in menu_list:
        rnd = choice(i)
        while rnd in menu_id:
            rnd = choice(i)
        menu_id.append(rnd)
    return menu_id


def add_to_favorite(u_id, name):
    con = sqlite3.connect("recipes_db.db")
    cur = con.cursor()
    rec_id = cur.execute("""SELECT id FROM recipes WHERE name=?""", (name.capitalize(),)).fetchone()
    if rec_id is not None:
        res = cur.execute("""SELECT favorite FROM users_information WHERE u_id=?""", (u_id,)).fetchone()
        if res:
            if str(rec_id[0]) not in res[0].split(';'):
                rec_ids = f"{res[0]};{rec_id[0]}"
                cur.execute("""UPDATE users_information SET favorite=? WHERE u_id=?""", (rec_ids, u_id)).fetchall()
            else:
                return 'Этот рецепт уже добавлен в избранное 🤔'
        else:
            cur.execute("""INSERT INTO users_information(u_id,favorite) VALUES(?,?)""", (u_id, rec_id[0])).fetchall()
        con.commit()
        con.close()
        return "Рецепт добавлен!"
    return "Такого рецепта у нас нет 😣"


def delete_from_favorite(u_id, name):
    con = sqlite3.connect("recipes_db.db")
    cur = con.cursor()
    rec_id = cur.execute("""SELECT id FROM recipes WHERE name=?""", (name.capitalize(),)).fetchone()
    if rec_id is not None:
        res = cur.execute("""SELECT favorite FROM users_information WHERE u_id=?""", (u_id,)).fetchone()
        if res[0] != '':
            if str(rec_id[0]) in res[0].split(';'):
                ids = res[0].split(';')
                del ids[ids.index(str(rec_id[0]))]
                rec_ids = ';'.join(ids)
                cur.execute("""UPDATE users_information SET favorite=? WHERE u_id=?""", (rec_ids, u_id)).fetchall()
                con.commit()
                con.close()
                return 'Рецепт убран!'
            else:
                return 'Этого рецепта нет в избранном 🤔'
        else:
            return 'У вас нет рецептов в избранном'
    return "Такого рецепта у нас нет 😣"


def favorite_list(u_id):
    con = sqlite3.connect("recipes_db.db")
    cur = con.cursor()
    res = cur.execute("""SELECT favorite FROM users_information WHERE u_id=?""", (u_id,)).fetchone()[0]
    if res != '':
        txt = 'Избранное:'
        for i in res.split(';'):
            if i != '':
                r = cur.execute("""SELECT name FROM recipes WHERE id=?""", (i,)).fetchone()[0]
                txt += f"\n— {r}"
        return txt
    else:
        return "В избранном ничего нет"
