import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random


def main():
    vk_session = vk_api.VkApi(
        token='a2467aba7103f6a9a6cbce79ea26aef5d8e5cfa8687f54cb633d3937798989a268b9dc005dcd646330d44')

    longpoll = VkBotLongPoll(vk_session, 204122708)

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            try:
                if event.obj.message['text'].isdigit():
                    if event.obj.message['text'] == '404':
                        raise ValueError
                    for i in range(int(event.obj.message['text'])):
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message=str(i),
                                         random_id=random.randint(0, 2 ** 64))
                print(event)
                print('Новое сообщение:')
                print('Для меня от:', event.obj.message['from_id'])
                print('Текст:', event.obj.message['text'])
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message="Спасибо, что написали нам. Мы обязательно ответим",
                                 random_id=random.randint(0, 2 ** 64))
            except ValueError:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message="Что-то не так",
                                 random_id=random.randint(0, 2 ** 64))
        if event.type == VkBotEventType.MESSAGE_TYPING_STATE:
            print(f'Печатает {event.obj.from_id} для {event.obj.to_id}')


if __name__ == '__main__':
    main()
