import os
import random
from codecs import decode
from functools import partial

import redis
import telegram
from dotenv import load_dotenv
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,

)
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

tg_logger = logging.getLogger(__name__)


def get_questions_and_answers(book_directory):
    questions_and_answers = {}
    for file in os.listdir(book_directory):
        with open(f"{book_directory}/{file}", "r", encoding='KOI8-R') as my_file:
            quiz = my_file.read()
        split_quiz = quiz.split('\n\n')
        for index, item in enumerate(split_quiz):
            question_number, *question = item.split(':')
            if question_number.startswith('Вопрос'):
                _, split_answer = split_quiz[index + 1].split('Ответ:\n')
                questions_and_answers[item] = split_answer
        return questions_and_answers


def start(bot, update):
    update.message.reply_text(f'Привет, {update.message.chat.username} \n Я бот для викторин!')


def send_question(bot, update, redis_db=None, questions_and_answers=None):
    keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет', ]
    ]

    if update.message.text == 'Новый вопрос':

        random_question = random.choice(list(questions_and_answers))
        bot.send_message(
            chat_id=update.message.chat.id,
            text=random_question,
            reply_markup=telegram.ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            )
        )
        redis_db.set(update.message.chat.id, questions_and_answers[random_question])
        answer = decode(redis_db.get(update.message.chat.id))
        without_point_answer, *_ = answer.split('.')
        without_parenthesis_answer, *_ = answer.split('(')
        print(without_point_answer)
        return update.message.text is False

    answer = decode(redis_db.get(update.message.chat.id))
    without_point_answer, *_ = answer.split('.')
    without_parenthesis_answer, *_ = answer.split('(')
    print(without_point_answer)

    if update.message.text.startswith(without_point_answer) or update.message.text.startswith(without_parenthesis_answer):
        bot.send_message(
            chat_id=update.message.chat.id,
            text='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
            reply_markup=telegram.ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            )
        )
        return update.message.text is True

    if update.message.text is not True:
        bot.send_message(
            chat_id=update.message.chat.id,
            text='Неправильно… Попробуешь ещё раз?',
            reply_markup=telegram.ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            )
        )


def error(bot, update, error):
    tg_logger.warning('Update "%s" caused error "%s"', update, error)


def main() -> None:
    load_dotenv()
    redis_db = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        db=0,
        password=os.getenv('REDIS_PASSWORD'),
    )
    questions_and_answers = get_questions_and_answers(os.getenv('QUIZ_QUESTIONS_FOLDER'))
    updater = Updater(os.getenv('TG_TOKEN'))

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))

    dp.add_handler(
        MessageHandler(
            Filters.text,
            partial(
                send_question,
                redis_db=redis_db,
                questions_and_answers=questions_and_answers
            )
        )
    )

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
