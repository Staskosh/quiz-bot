import os


def get_questions_and_answers(book_directory):
    questions_and_answers = {}
    for file in os.listdir(book_directory):
        with open(f'{book_directory}/{file}', 'r', encoding='KOI8-R') as my_file:
            quiz = my_file.read()
        split_quiz = quiz.split('\n\n')
        for index, item in enumerate(split_quiz):
            question_number, *question = item.split(':')
            if question_number.startswith('Вопрос'):
                _, split_answer = split_quiz[index + 1].split('Ответ:\n')
                questions_and_answers[item] = split_answer

        return questions_and_answers
