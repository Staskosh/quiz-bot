import os
import random

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
                questions_and_answers[item] = split_quiz[index + 1]
        return questions_and_answers


def start(bot, update):
    update.message.reply_text(f'Hi {update.message.chat.username}!')


def send_question(bot, update):
    text = "Привет, я бот для викторин"
    redis_db = redis.Redis(
        host='redis-15822.c300.eu-central-1-1.ec2.cloud.redislabs.com',
        port=os.getenv('REDIS_PORT'),
        db=0,
        password='sC8nM6txxSrE9nZuosfQp0PpWv9n3bOD',
    )
    keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет', ]
    ]
    update.message.reply_text(
        text,
        reply_markup=telegram.ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
        )
    )
    if update.message.text == 'Новый вопрос':
        questions_and_answers = get_questions_and_answers(os.getenv('QUIZ_QUESTIONS_FOLDER'))
        random_question = random.choice(list(questions_and_answers))
        bot.send_message(
            chat_id=update.message.chat.id,
            text=random_question,
            reply_markup=telegram.ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            )
        )
        redis_db.set(update.message.chat.id, random_question)
        redis_db.get(update.message.chat.id)


def error(bot, update, error):
    tg_logger.warning('Update "%s" caused error "%s"', update, error)


def main() -> None:
    load_dotenv()

    updater = Updater(os.getenv('TG_TOKEN'))

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))

    dp.add_handler(MessageHandler(Filters.text, send_question))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
