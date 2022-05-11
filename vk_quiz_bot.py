import os

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

tg_logger = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text(f'Hi {update.message.chat.username}!')


def echo(bot, update):
    update.message.reply_text(update.message.text)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def get_questions_and_answers(book_directory):
    questions_and_answers = {}
    for file in os.listdir(book_directory):
        with open(f"{book_directory}/{file}", "r", encoding='KOI8-R') as my_file:
            quiz = my_file.read()
        split_quiz = quiz.split('\n\n')
        for index, item in enumerate(split_quiz):
            question_number, *question = item.split(':')
            if question_number.startswith('Вопрос'):
                questions_and_answers[item] = split_quiz[index+1]
        return questions_and_answers


def main() -> None:
    load_dotenv()
    book_directory = os.getenv('QUIZ_QUESTIONS_FOLDER')
    questions_and_answers = get_questions_and_answers(book_directory)
    updater = Updater(os.getenv("TG_TOKEN"))

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
