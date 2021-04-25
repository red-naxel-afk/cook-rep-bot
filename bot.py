import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import time
import random

from function import *


def send_message(vk, event, message):
    vk.messages.send(user_id=event.obj.message['from_id'],
                     message=message,
                     random_id=random.randint(0, 2 ** 64))


def recipes_message(id_r):
    con = sqlite3.connect("recipes_db.db")
    cur = con.cursor()

    result = cur.execute("""SELECT name, ingredients, ingredients_count, steps, time, tags, video_url FROM recipes 
                            WHERE id = {}""".format(str(id_r))).fetchall()[0]
    con.close()
    mes = "Рецепт: " + result[0] + " \n\nИнгредиенты: \n"

    ing_list = result[1].split(';')
    count_list = result[2].split(';')
    steps_list = result[3].split(';')
    cooking_time = result[4]
    tags = result[5].split(';')
    url = result[6]

    for ing in range(len(ing_list)):
        mes += '-- ' + ing_list[ing]

        if count_list[ing] != '-':
            mes += ' - ' + count_list[ing]
        mes += '\n'

    mes += '\nПриготовление: \n\n'

    for step in steps_list:
        mes += "-- " + step + '\n'

    mes += "\nВремя приготовления: " + cooking_time + '\n\n'

    mes += "Теги: \n"

    for tag in tags:
        mes += "-- " + tag + '\n'

    mes += "\nВидео: \n"
    mes += '\n' + url

    return mes


def main():
    with open('C:/Users/Alex/Desktop/k.txt', 'r') as f:
        key = f.read()

    vk_session = vk_api.VkApi(
        token=key)

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
                    users_states[user_id] = ['', -1, []]  # состояние, время таймера

                if users_states[user_id][0] == '':  # если пользователь ничего не сделал
                    if text == 'помощь':
                        mes = '''Помощь           - показывает это сообщение
                                 ~------------------------------------------------------
                                 Поиск            - позволяет найти нужный рецепт
                                 Случайный рецепт - выводит случайный рецепт
                                 Меню дня         - выводит меню, созданное для этого дня
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
                                                   Название   - поиск рецепта по названию
                                                   Например: Название <позиция>
                                                   ~------------------------------------------------------
                                                   Тег - поиск рецепта по тегу
                                                   Например: Тег <позиция, позиция>
                                                   ~------------------------------------------------------
                                                   ингредиент   - поиск рецепта по ингредиент
                                                   Например: ингредиенты <позиция, позиция>
                                                   ~------------------------------------------------------
                                                   Отмена   - выход из режима поиска''')
                    elif text == 'случайный рецепт':
                        random_recipes_id = random_recipes()
                        send_message(vk, event, recipes_message(random_recipes_id))
                    elif text == 'меню дня':
                        pass
                    elif text == 'таймер':
                        users_states[user_id][0] = 'setting_timer'
                        send_message(vk, event, 'На сколько секунд?')
                    elif text == 'время':
                        if users_states[user_id][1] != -1:
                            seconds_to_over = int(users_states[user_id][1] - time.time())

                            out = str(seconds_to_over % 60) + 'секунд'

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
                        pass
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
                    else:
                        send_message(vk, event, '''Неизвестное мне сообщение
                        Посмотреть мои функции можно введя "Помощь"''')
                elif users_states[user_id][0] == 'setting_timer':  # если пользователь заводит таймер
                    if text == 'отмена':
                        send_message(vk, event, 'Отменено')
                        users_states[user_id][0] = ''
                    else:
                        try:
                            users_states[user_id][1] = int(int(text) + time.time())
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
                                                   Убрать   - убирает позицию из списка 
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
                                                   Название   - поиск рецепта по названию
                                                   Например: Название <позиция>
                                                   ~------------------------------------------------------
                                                   Тег - поиск рецепта по тегу
                                                   Например: Тег <позиция, позиция>
                                                   ~------------------------------------------------------
                                                   ингредиент   - поиск рецепта по ингредиент
                                                   Например: ингредиенты <позиция, позиция>
                                                   ~------------------------------------------------------
                                                   Отмена   - выход из режима поиска''')
                    elif text.split()[0] == 'название':
                        if len(text.split()) == 1:
                            send_message(vk, event, 'Пожалуйста укажите позицию')
                        else:
                            con = sqlite3.connect("recipes_db.db")

                            cur = con.cursor()
                            result = cur.execute(
                                """SELECT id FROM recipes WHERE name = '{}'""".format(text.split()[1])).fetchall()
                            print(result)
                            con.close()

                            send_message(vk, event, 'Добавлено в список: ' + text.split()[1])
                    elif text.split()[0] == 'тег':
                        if len(text.split()) == 1:
                            send_message(vk, event, 'Пожалуйста укажите позицию')
                        else:
                            users_states[user_id][2].append(text.split()[1])
                            send_message(vk, event, 'Добавлено в список: ' + text.split()[1])
                    else:
                        send_message(vk, event, '''Неизвестное мне сообщение
                                                Посмотреть мои функции можно введя "Помощь"''')


if __name__ == '__main__':
    main()
