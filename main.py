import requests
import os
from datetime import datetime
import re


USERS_URL = 'https://json.medrating.org/users'
TODOS_URL = 'https://json.medrating.org/todos'
BASE_PATH = os.getcwd()
TASKS_PATH = BASE_PATH + '\\tasks\\'


users_tasks = {}


def create_file(user) -> None:
    """
    Функция создания файла для пользователя
    :param user: словарь данных пользователя
    :return: None
    """
    text_field = ''  # Формирование содержимого файла
    text_field += f"Отчет для {user['company']['name']}.\n"  # Первая строка
    text_field += f"{user['name']} < {user['email']}> "  # Вторая строка

    current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
    text_field += f"{current_date}\n"  # Добавление даты в нужном формате

    completed_tasks, left_tasks = users_tasks[user['id']]
    completed_tasks_count, left_tasks_count = len(completed_tasks), len(left_tasks)

    text_field += f"Всего задач: {completed_tasks_count + left_tasks_count}\n"  # Третья строка
    text_field += f"\nЗавершенные задачи ({completed_tasks_count}):\n"
    text_field += str([f"{completed_task}\n" for completed_task in completed_tasks])
    text_field += f"\nОставшиеся задачи ({left_tasks_count}):\n"
    text_field += str([f"{left_task}\n" for left_task in left_tasks])

    with open(f"{TASKS_PATH}{user['username']}.txt", 'w') as new_file:
        new_file.write(text_field)


def rename_file(old_name) -> None:
    """
    Функция которая переименовывает исходный файл
    :param old_name: первоначальное имя файла (пользователя без txt)
    :return: None
    """
    old_path = f"{TASKS_PATH}{old_name}.txt"
    with open(old_path, 'r') as file:
        text = file.read()

    old_time = re.search(r"> (.*)\n", text).group(1)
    # old_time = "".join(['-' if c in ['.', ':'] else 'T' if c == ' ' else c for c in old_time])
    time_fixed = ''
    for letter in old_time:
        if letter in ['.',':']:
            time_fixed += '-'
        elif letter == ' ':
            time_fixed += 'T'
        else:
            time_fixed += letter
    new_path = f"{TASKS_PATH}old_{old_name}_{time_fixed}.txt"
    try:
        os.rename(old_path, new_path)
    except FileExistsError:
        pass


def create_dir() -> bool:
    """
    Функция создания директории, если ее еще нет
    :return: True если директория успешно создана, False иначе
    """
    try:
        os.mkdir(TASKS_PATH)
    except OSError:
        return False
    else:
        return True


def fill_users_tasks() -> None:
    """
    Функция заполнения структуры users_tasks {'id': ([tasks_completed][tasks_left])}
    :return: None
    """
    tasks_list = requests.get(TODOS_URL).json()
    for task in tasks_list:
        try:
            task_title = task['title'] if len(task['title']) <= 48 else f"{task['title'][0:48]}..."
            # Добавление первых 48 символов и затем троеточия
            new_tasks = users_tasks.get(task['userId'], ([], []))
            new_tasks[0 if task['completed'] else 1].append(task_title)
            users_tasks.update({task['userId']: new_tasks})
        except KeyError:
            pass


def create_report() -> None:
    """
    Функция создания отчета
    :return:
    """
    users_list = requests.get(USERS_URL).json()
    fill_users_tasks()
    if create_dir():
        for user in users_list:
            create_file(user)
    else:
        print('Директория уже есть')
        for user in users_list:
            if os.path.exists(f"{TASKS_PATH}{user['username']}.txt"):
                rename_file(user['username'])
            create_file(user)


def main():
    date1 = datetime.now()
    fill_users_tasks()
    create_report()
    print(datetime.now() - date1)


if __name__ == '__main__':
    main()
