import os

from dotenv import load_dotenv


def get_questions(book_directory):
    with open(f"{book_directory}/1vs1200.txt", "r", encoding='KOI8-R') as my_file:
        quiz = my_file.read()
    print(quiz)


def main() -> None:
    load_dotenv()
    book_directory = os.getenv('QUIZ_QUESTIONS_FOLDER')
    get_questions(book_directory)


if __name__ == '__main__':
    main()
