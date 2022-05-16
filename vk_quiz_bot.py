import os
import random
from codecs import decode

import redis
import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType

# def get_response(event, vk_api):
#     vk_api.messages.send(
#         user_id=event.user_id,
#         message=event.text,
#         keyboard=keyboard.get_keyboard(),
#         random_id=random.randint(1,1000)
#     )
from get_answers_and_questions import get_questions_and_answers


def main() -> None:
    load_dotenv()
    redis_db = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        db=0,
        password=os.getenv('REDIS_PASSWORD'),
    )
    questions_and_answers = get_questions_and_answers(os.getenv('QUIZ_QUESTIONS_FOLDER'))
    vk_session = vk.VkApi(token=os.getenv('VK_TOKEN'))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос')
    keyboard.add_button('Сдаться')

    keyboard.add_line()

    keyboard.add_button('Мой счет')

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            vk_api.messages.send(
                user_id=event.user_id,
                message=f'Привет, {event.user_id} \n Я бот для викторин!',
                keyboard=keyboard.get_keyboard(),
                random_id=random.randint(1, 1000)
            )

            if event.text == "Новый вопрос":
                random_question = random.choice(list(questions_and_answers))
                vk_api.messages.send(
                    user_id=event.user_id,
                    message=random_question,
                    keyboard=keyboard.get_keyboard(),
                    random_id=random.randint(1, 1000)
                )

                redis_db.set(event.user_id, questions_and_answers[random_question])

                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                        answer = decode(redis_db.get(event.user_id))
                        without_point_answer, *_ = answer.split('.')
                        without_parenthesis_answer, *_ = answer.split('(')
                        print(answer)

                        if event.text.startswith(without_point_answer) or event.text.startswith(
                                without_parenthesis_answer):
                            vk_api.messages.send(
                                user_id=event.user_id,
                                message='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
                                keyboard=keyboard.get_keyboard(),
                                random_id=random.randint(1, 1000)
                            )
                            break

                        if event.text == "Сдаться":
                            vk_api.messages.send(
                                user_id=event.user_id,
                                message=f'Правильный ответ {answer}. Для следующего вопроса нажми «Новый вопрос»',
                                keyboard=keyboard.get_keyboard(),
                                random_id=random.randint(1, 1000)
                            )
                            break

                        if event.text:
                            vk_api.messages.send(
                                user_id=event.user_id,
                                message='Неправильно… Попробуешь ещё раз?',
                                keyboard=keyboard.get_keyboard(),
                                random_id=random.randint(1, 1000)
                            )


if __name__ == "__main__":
    main()
