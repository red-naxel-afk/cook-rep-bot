import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import time
import random
import requests

from function import *


def main():
    vk_session = vk_api.VkApi(
        token='8b1b7cf17ac165f837a7282120e6d616cd6a4ed0a167fe81bdd6e9d7db4c7a59f81d1d419120f2c70f348')

    longpoll = VkBotLongPoll(vk_session, 204122708, wait=1)
    vk = vk_session.get_api()

    users_states = {}
    while True:
        for i in users_states:  # проверка срабатывания таймера
            if users_states[i][1] != -1 and users_states[i][1] <= time.time():
                vk.messages.send(user_id=i,
                                 message='Тик-так! Время вышло!',
                                 random_id=random.randint(0, 2 ** 64))
                users_states[i][1] = -1

        for event in longpoll.check():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id = event.obj.message['from_id']
                text = event.obj.message['text'].lower()

                if user_id not in users_states:
                    users_states[user_id] = ['', -1, [], {'identical_recipes': [],
                                                          'similar_recipes': []}]  # состояние, время таймера

                if users_states[user_id][0] == '':  # если пользователь ничего не сделал
                    if text == 'помощь':
                        mes = '''Помощь           - показывает это сообщение
                        ~------------------------------------------------------
                        Поиск            - позволяет найти нужный рецепт
                        Случайный рецепт - выводит случайный рецепт
                        Случайное меню   - выводит случайное меню
                        Случайное постное меню - выводит случайное постное меню
                        Избранное        - позболяет добавить рецепт в избранное
                        ~-------------------------------------------------------
                        Таймер           - заводит таймер
                        Время            - показывает сколько времени осталось
                        Прервать         - останавливает таймер
                        ~------------------------------------------------------
                        Магазины         - показывает ближайшие магазины
                        Список           - показывает список покупок
                        Изменить         - открывает меню изменения списка покупок'''
                        send_message(vk, event, mes)
                    elif text == 'поиск':
                        users_states[user_id][0] = 'search'
                        send_message(vk, event, '''Помощь   - выводит это сообщение
                        ~------------------------------------------------------
                        Рецепт   - поиск рецепта по названию
                        Например: Название <позиция>
                        ~------------------------------------------------------
                        Тег - поиск рецепта по тегу
                        Например: Тег <позиция, позиция>
                        ~------------------------------------------------------
                        Ингредиент   - поиск рецепта по ингредиент
                        Например: ингредиенты <позиция, позиция>
                        ~------------------------------------------------------
                        Отмена   - выход из режима поиска''')
                    elif text == 'случайный рецепт':
                        random_recipes_id = random_recipes()
                        send_message(vk, event, recipes_message(random_recipes_id))
                    elif text == 'случайное меню':
                        menu_id = daily_menu()
                        menu_names = list()
                        for i in menu_id:
                            con = sqlite3.connect("recipes_db.db")
                            cur = con.cursor()
                            result = cur.execute("""SELECT name FROM recipes WHERE id=?""", (i,)).fetchall()
                            menu_names.append(result[0])
                            con.close()
                        menu = f"Случайное меню:\nЗавтрак:\n-{menu_names[0][0]}\n-{menu_names[1][0]}" \
                               f"\nОбед:\n-{menu_names[2][0]}" \
                               f"\nПерекус:\n  -{menu_names[3][0]}" \
                               f"\nУжин:\n  -{menu_names[4][0]}\n-{menu_names[5][0]}\n-{menu_names[6][0]}" \
                               f"\n~------------------------------------------------------" \
                               f"\nДля нахождения блюда воспользуйтесь поиском 🔎"
                        send_message(vk, event, menu)
                    elif text == 'случайное постное меню':
                        menu_id = vegetarian_menu()
                        menu_names = list()
                        for i in menu_id:
                            con = sqlite3.connect("recipes_db.db")
                            cur = con.cursor()
                            result = cur.execute("""SELECT name FROM recipes WHERE id=?""", (i,)).fetchall()
                            menu_names.append(result[0])
                            con.close()
                        menu = f"Вегетарианское случайное меню:\nЗавтрак:\n-{menu_names[0][0]}\n-{menu_names[1][0]}" \
                               f"\nОбед:\n-{menu_names[2][0]}" \
                               f"\nПерекус:\n  -{menu_names[3][0]}" \
                               f"\nУжин:\n  -{menu_names[4][0]}\n-{menu_names[5][0]}" \
                               f"\n~------------------------------------------------------" \
                               f"\nДля нахождения блюда воспользуйтесь поиском 🔎"
                        send_message(vk, event, menu)
                    elif text == 'таймер':
                        users_states[user_id][0] = 'setting_timer'
                        send_message(vk, event, 'На сколько минут?')
                    elif text == 'время':
                        if users_states[user_id][1] != -1:
                            seconds_to_over = int(users_states[user_id][1] - time.time())

                            out = ''

                            if seconds_to_over % 60 != 0:
                                out += str(seconds_to_over % 60) + 'секунд'

                            if seconds_to_over // 60 > 0:
                                out = str((seconds_to_over // 60) % 60) + ' минут ' + out

                            if (seconds_to_over // 60) // 60 > 0:
                                out = str((seconds_to_over // 60) // 60) + ' часов ' + out

                            send_message(vk, event, 'Осталось: ' + out)
                        else:
                            send_message(vk, event, 'Таймер не заведен')
                    elif text == 'прервать':
                        if users_states[user_id][1] != -1:
                            users_states[user_id][1] = -1
                            send_message(vk, event, 'Таймер остановлен')
                        else:
                            send_message(vk, event, 'Таймер не заведен')
                    elif text == 'магазины':
                        users_states[user_id][0] = 'mag_search'
                        send_message(vk, event, 'Введите ваш адрес')
                    elif text == 'список':
                        if not users_states[user_id][2]:
                            send_message(vk, event, 'Список покупок пуст')
                        else:
                            send_message(vk, event, '-- ' + '\n-- '.join(users_states[user_id][2]))
                    elif text == 'изменить':
                        users_states[user_id][0] = 'buy_list_edit'
                        send_message(vk, event, '''Помощь   - выводит это сообщение
                                                   ~------------------------------------------------------
                                                   Добавить - добавляет позицию в список
                                                   Например: Добавить <позиция>
                                                   ~------------------------------------------------------
                                                   Убрать   - убирает позицию из списка 
                                                   Например: Убрать <позиция>
                                                   ~------------------------------------------------------
                                                   Отмена   - выход из режима изменения''')
                    elif text == 'избранное':
                        users_states[user_id][0] = 'favorite'
                        send_message(vk, event, '''Помощь   - выводит это сообщение
                        ~------------------------------------------------------
                        Добавить   - добавляет рецепт в избранное
                        Например: Добавить <позиция>
                        ~------------------------------------------------------
                        Убрать   - убирает рецепт из избранного
                        Например: Убрать <позиция>
                        ~------------------------------------------------------
                        Посмотреть избранное - показывает избранные рецепты
                        ~------------------------------------------------------
                        Отмена   - выход из режима избранного''')
                    else:
                        send_message(vk, event, '''Неизвестное мне сообщение
                        Посмотреть мои функции можно введя "Помощь"''')
                elif users_states[user_id][0] == 'setting_timer':  # если пользователь заводит таймер
                    if text == 'отмена':
                        send_message(vk, event, 'Отменено')
                        users_states[user_id][0] = ''
                    else:
                        try:
                            users_states[user_id][1] = int(int(float(text) * 60) + time.time())
                            users_states[user_id][0] = ''
                            send_message(vk, event, 'Таймер заведен!')
                        except ValueError:
                            send_message(vk, event, '''Неправильный ввод, попробуй еще
                            Чтобы выйти напиши "Отмена"''')
                elif users_states[user_id][0] == 'buy_list_edit':
                    if text == 'отмена':
                        send_message(vk, event, 'Отменено')
                        users_states[user_id][0] = ''
                    elif text == 'помощь':
                        send_message(vk, event, '''Помощь   - выводит это сообщение
                        ~------------------------------------------------------
                        Добавить - добавляет позицию в список
                        Например: Добавить <позиция>
                        ~------------------------------------------------------
                        брать   - убирает позицию из списка 
                        Например: Убрать <позиция>
                        ~------------------------------------------------------
                        Отмена   - выход из режима изменения''')
                    elif text.split()[0] == 'добавить':
                        if len(text.split()) == 1:
                            send_message(vk, event, 'Пожалуйста укажите позицию')
                        else:
                            users_states[user_id][2].append(text.split()[1])
                            send_message(vk, event, 'Добавлено в список: ' + text.split()[1])
                    elif text.split()[0] == 'убрать':
                        if len(text.split()) == 1:
                            send_message(vk, event, 'Пожалуйста укажите позицию')
                        else:
                            if text.split()[1] in users_states[user_id][2]:
                                del users_states[user_id][2][users_states[user_id][2].index(text.split()[1])]
                                send_message(vk, event, 'Удалено из списка: ' + text.split()[1])
                            else:
                                send_message(vk, event, 'В списке продуктов нет такой позиции')
                    else:
                        send_message(vk, event, '''Неизвестное мне сообщение
                                                Посмотреть мои функции можно введя "Помощь"''')
                elif users_states[user_id][0] == 'search':
                    if text == 'отмена':
                        send_message(vk, event, 'Отменено')
                        users_states[user_id][0] = ''
                    elif text == 'помощь':
                        send_message(vk, event, '''Помощь   - выводит это сообщение
                        ~------------------------------------------------------
                        Рецепт   - поиск рецепта по названию
                        Например: Название <позиция>
                        ~------------------------------------------------------
                        Тег - поиск рецепта по тегу
                        Например: Тег <позиция, позиция>
                        ~------------------------------------------------------
                        Ингредиент   - поиск рецепта по ингредиент
                        Например: ингредиенты <позиция, позиция>
                        ~------------------------------------------------------
                        Отмена   - выход из режима поиска''')
                    elif text.split()[0] == 'рецепт':
                        if len(text.split()) == 1:
                            send_message(vk, event, 'Пожалуйста укажите позицию')
                        else:
                            name = text.split()[1:]

                            name = ' '.join(name).capitalize()

                            con = sqlite3.connect("recipes_db.db")

                            cur = con.cursor()
                            result = cur.execute("""SELECT id FROM recipes 
                            WHERE name = '{}'""".format(name)).fetchall()
                            con.close()

                            if len(result) != 0:
                                send_message(vk, event, recipes_message(result[0][0]))
                            else:
                                send_message(vk, event, 'Такого рецепта не нашлось')

                    elif text.split()[0] == 'тег':
                        if len(text.split()) == 1:
                            send_message(vk, event, 'Пожалуйста укажите позицию')
                        else:
                            tags = text.split()[1:]
                            tags = ' '.join(tags).split(', ')

                            tags = ';'.join(tags)

                            identical_recipes, similar_recipes = tags_search(tags)

                            if len(identical_recipes) == 0 and len(similar_recipes) == 0:
                                send_message(vk, event, '''Таких рецептов нет
                                                           Убедитесь, что введены правильные теги''')
                            else:
                                mes = ''
                                if len(identical_recipes) == 0:
                                    mes += 'Рецептов с введёнными тегами нет \n\n'
                                else:
                                    mes += 'Рецепты только с введёнными тегами: \n\n'

                                    for r in identical_recipes:
                                        mes += '-- ' + r[1] + '\n'

                                    mes += '\n'

                                if len(similar_recipes) == 0:
                                    mes += 'Рецептов и с другими тегами нет\n\n'
                                else:
                                    mes += 'Рецепты и с другими тегами: \n\n'

                                    for r in similar_recipes:
                                        mes += '-- ' + r[1] + '\n'

                                    mes += '\n\n'

                                    mes += 'Для нахождения блюда воспользуйтесь поиском 🔎'

                                send_message(vk, event, mes)
                    elif text.split()[0] == 'ингредиент':
                        if len(text.split()) == 1:
                            send_message(vk, event, 'Пожалуйста укажите позицию')
                        else:
                            ing = text.split()[1:]
                            ing = ' '.join(ing).split(', ')

                            ing = ';'.join(ing)

                            identical_recipes, similar_recipes = ingredients_search(ing)

                            if len(identical_recipes) == 0 and len(similar_recipes) == 0:
                                send_message(vk, event, '''Таких рецептов нет
                                                           Убедитесь, что введены правильные ингредиенты''')
                            else:
                                mes = ''
                                if len(identical_recipes) == 0:
                                    mes += 'Рецептов с введёнными ингредиентами нет \n\n'
                                else:
                                    mes += 'Рецепты только с введёнными ингредиентами: \n\n'

                                    for r in identical_recipes:
                                        mes += '-- ' + r[1] + '\n'

                                    mes += '\n'

                                if len(similar_recipes) == 0:
                                    mes += 'Рецептов и с другими ингредиентами нет\n\n'
                                else:
                                    mes += 'Рецепты и с другими ингредиентами: \n\n'

                                    for r in similar_recipes:
                                        mes += '-- ' + r[1] + '\n'

                                    mes += '\n\n'

                                    mes += 'Для нахождения блюда воспользуйтесь поиском 🔎'

                                send_message(vk, event, mes)

                    else:
                        send_message(vk, event, '''Неизвестное мне сообщение
                                                Посмотреть мои функции можно введя "Помощь"''')
                elif users_states[user_id][0] == 'favorite':
                    if text == 'отмена':
                        send_message(vk, event, 'Отменено')
                        users_states[user_id][0] = ''
                    elif text == 'помощь':
                        send_message(vk, event, '''Помощь   - выводит это сообщение
                        ~------------------------------------------------------
                        Добавить   - добавляет рецепт в избранное
                        Например: Добавить <позиция>
                        ~------------------------------------------------------
                        Убрать   - убирает рецепт из избранного
                        Например: Убрать <позиция>
                        ~------------------------------------------------------
                        Отмена   - выход из режима избранного''')
                    elif text.split()[0] == 'добавить':
                        if len(text.split()) == 1:
                            send_message(vk, event, 'Пожалуйста укажите позицию')
                        else:
                            name = text.split()[1:]
                            name = ' '.join(name).capitalize()
                            res = add_to_favorite(user_id, name)
                            send_message(vk, event, res)
                    elif text.split()[0] == 'убрать':
                        if len(text.split()) == 1:
                            send_message(vk, event, 'Пожалуйста укажите позицию')
                        else:
                            name = text.split()[1:]
                            name = ' '.join(name).capitalize()
                            res = delete_from_favorite(user_id, name)
                            send_message(vk, event, res)
                    elif text == 'посмотреть избранное':
                        send_message(vk, event, favorite_list(user_id))
                    else:
                        send_message(vk, event, '''Неизвестное мне сообщение
                                                Посмотреть мои функции можно введя "Помощь"''')
                elif users_states[user_id][0] == 'mag_search':
                    ad = text.lower()

                    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?"
                    geocoder_request += "apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" + ad + "&format=json"

                    response = requests.get(geocoder_request)
                    if response:
                        json_response = response.json()

                        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

                        toponym_coodrinates = toponym["Point"]["pos"]

                        toponym_coodrinates = toponym_coodrinates.split(' ')

                        toponym_coodrinates = ','.join(toponym_coodrinates)

                        search_api_server = "https://search-maps.yandex.ru/v1/"
                        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

                        address_ll = toponym_coodrinates

                        search_params = {
                            "apikey": api_key,
                            "text": "магазин",
                            "lang": "ru_RU",
                            "ll": address_ll,
                            "type": "biz"
                        }

                        response = requests.get(search_api_server, params=search_params)

                        if response:

                            json_response = response.json()

                            mes = '~-------------------------------------------------------\n'

                            for i in json_response["features"]:
                                toponym_name = i["properties"]["CompanyMetaData"]["name"]

                                toponym_address = i["properties"]["CompanyMetaData"]["address"]
                                toponym_time = i["properties"]["CompanyMetaData"]["Hours"]["text"]

                                mes += toponym_name + '\n'
                                mes += ' '.join(toponym_address.split(', ')[2:]) + '\n'
                                mes += toponym_time + '\n'
                                mes += '~-------------------------------------------------------\n'
                            send_message(vk, event, mes)
                        else:
                            send_message(vk, event, 'Упс! Похоже что-то сломалось')
                    else:
                        send_message(vk, event, 'Упс! Похоже что-то сломалось')
                    users_states[user_id][0] = ''


if __name__ == '__main__':
    main()
