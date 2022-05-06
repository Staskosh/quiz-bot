import os

from dotenv import load_dotenv


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


if __name__ == '__main__':
    main()
