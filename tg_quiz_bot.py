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
    Filters, ConversationHandler, RegexHandler,

)
import logging

from get_answers_and_questions import get_questions_and_answers

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

tg_logger = logging.getLogger(__name__)

QUESTION, ANSWER, CANCEL = range(3)

keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет', ]
    ]


def start(bot, update):
    update.message.reply_text(
        f'Привет, {update.message.chat.username} \n Я бот для викторин!',
        reply_markup=telegram.ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
        )
    )

    return QUESTION


def handle_new_question_request(bot, update, redis_db=None, questions_and_answers=None):
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

    return ANSWER


def handle_solution_attempt(bot, update, redis_db=None):
    answer = decode(redis_db.get(update.message.chat.id))
    without_point_answer, *_ = answer.split('.')
    without_parenthesis_answer, *_ = answer.split('(')

    if update.message.text.startswith(without_point_answer) or update.message.text.startswith(
            without_parenthesis_answer):
        bot.send_message(
            chat_id=update.message.chat.id,
            text='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
            reply_markup=telegram.ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            )
        )
        update.message.text = True
        return QUESTION

    if update.message.text is not True and update.message.text != 'Сдаться':
        bot.send_message(
            chat_id=update.message.chat.id,
            text='Неправильно… Попробуешь ещё раз?',
            reply_markup=telegram.ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            )
        )
        return ANSWER


def give_up(bot, update, redis_db=None):
    answer = decode(redis_db.get(update.message.chat.id))
    bot.send_message(
        chat_id=update.message.chat.id,
        text=f'Правильный ответ {answer}. Для следующего вопроса нажми «Новый вопрос»',
        reply_markup=telegram.ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
        )
    )

    return QUESTION


def cancel(bot, update):
    bot.send_message(
        chat_id=update.message.chat.id,
        text='Для следующего вопроса нажми «Новый вопрос»',
        reply_markup=telegram.ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
        )
    )

    return QUESTION


def error(bot, update, error):
    tg_logger.warning(f'Update {update} caused error {error}')


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

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [RegexHandler('Новый вопрос',
                                    partial(
                                        handle_new_question_request,
                                        redis_db=redis_db,
                                        questions_and_answers=questions_and_answers
                                    )
                                    ),
                       ],

            ANSWER: [RegexHandler('Сдаться', partial(give_up, redis_db=redis_db,)),
                     MessageHandler(Filters.text,
                                    partial(
                                        handle_solution_attempt,
                                        redis_db=redis_db,
                                    )
                                    ),

                     ],
        },
        fallbacks=[RegexHandler('Сдаться', partial(cancel))]
    )
    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
