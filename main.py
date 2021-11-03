import requests
import os
from datetime import datetime
import re


USERS_URL = 'https://json.medrating.org/users'
TODOS_URL = 'https://json.medrating.org/todos'
BASE_PATH = os.getcwd()
TASKS_PATH = BASE_PATH + '\\tasks\\'


users_tasks = {}


def get_response(url: str) -> list:
    """
    Функция получения данных по URL с обработкой ошибок
    :param url: URL запроса
    :return: список словарей информации о пользователях/задачах
    """
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        raise Exception('Ошибка получения данных запроса')


def create_file(user: dict):
    """
    Функция создания файла для пользователя
    :param user: словарь данных пользователя
    """
    global users_tasks

    text_field = ''  # Формирование содержимого файла
    text_field += f"Отчет для {user['company']['name']}.\n"  # Первая строка
    text_field += f"{user['name']} <{user['email']}> "  # Вторая строка

    current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
    text_field += f"{current_date}\n"  # Добавление даты в нужном формате
    text_field += f"Всего задач: "
    if user['id'] in users_tasks.keys():
        completed_tasks, left_tasks = users_tasks[user['id']]
        completed_tasks_count, left_tasks_count = len(completed_tasks), len(left_tasks)

        text_field += f"{completed_tasks_count + left_tasks_count}\n"  # Третья строка
        text_field += f"\nЗавершенные задачи ({completed_tasks_count}):\n"
        text_field += "".join([f"{completed_task}\n" for completed_task in completed_tasks])
        # for completed_task in completed_tasks:
        #     text_field += f"{completed_task}\n"

        text_field += f"\nОставшиеся задачи ({left_tasks_count}):\n"
        text_field += "".join([f"{left_task}\n" for left_task in left_tasks])
        # for left_task in left_tasks:
        #     text_field += f"{left_task}\n"
    else:  # Обработка отсутствия задач у пользователя
        text_field += '0'

    with open(os.path.join(TASKS_PATH, user['username'] + '.txt'), 'w') as new_file:
        new_file.write(text_field)


def rename_file(old_name: str):
    """
    Функция которая переименовывает исходный файл
    :param old_name: первоначальное имя файла (пользователя без txt)
    """
    old_path = os.path.join(TASKS_PATH, old_name + '.txt')
    with open(old_path, 'r') as file:
        text = file.read()

    old_time = re.search(r"> (.*)\n", text).group(1)  # Поиск даты в отчете
    time_fixed = datetime.strptime(old_time, '%d.%m.%Y %H:%M').strftime('%d-%m-%YT%H-%M')  # Смена формата даты
    new_path = f"{TASKS_PATH}old_{old_name}_{time_fixed}.txt"
    try:
        os.rename(old_path, new_path)
    except FileExistsError:
        # print(f"Файл с именем {old_path} отсутствует и будет создан заново")
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


def fill_users_tasks():
    """
    Функция заполнения структуры users_tasks {'id': ([tasks_completed][tasks_left])}
    """
    global users_tasks
    tasks_list = get_response(TODOS_URL)
    for task in tasks_list:
        try:
            task_title = task['title'] if len(task['title']) <= 48 else f"{task['title'][0:48]}..."
            # Добавление первых 48 символов и затем троеточия
            new_tasks = users_tasks.get(task['userId'], ([], []))
            new_tasks[0 if task['completed'] else 1].append(task_title)
            users_tasks.update({task['userId']: new_tasks})
        except KeyError as e:
            print(f"В записи отсутствует поле {e.args[0]}")


def create_report():
    """
    Функция создания отчета
    """
    users_list = get_response(USERS_URL)
    fill_users_tasks()
    if create_dir():
        for user in users_list:
            create_file(user)
    else:
        for user in users_list:
            if os.path.exists(os.path.join(TASKS_PATH, user['username'] + '.txt')):
                rename_file(user['username'])
            create_file(user)


def main():
    create_report()


if __name__ == '__main__':
    main()
