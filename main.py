import requests
import os
from datetime import datetime
import re


USERS_URL = 'https://json.medrating.org/users'
TODOS_URL = 'https://json.medrating.org/todos'
BASE_PATH = os.getcwd()
TASKS_PATH = BASE_PATH + '\\tasks\\'


def get_info(url) -> list:
    """
    Функция получения данных по URL
    :param url: URL адрес в формате string
    :return: список словарей данных
    """
    return requests.get(url).json()


def get_tasks_count(_id, tasks) -> int:
    """
    Функция получения общего количества задач заданного пользователя
    :param _id: id проверяемого пользователя
    :param tasks: список словарей заданий пользователей
    :return: количество заданий проверяемого пользователя
    """
    count = 0
    for task in tasks:
        try:
            if task['userId'] == _id:
                count += 1
        except KeyError:
            pass
    return count


def get_tasks_completed(_id, tasks) -> list:
    """
    Функция получения списка выполненных задач заданного пользователя
    :param _id: id проверяемого пользователя
    :param tasks: список словарей заданий пользователей
    :return: список выполненных заданий проверяемого пользователя
    """
    task_list = []
    for task in tasks:
        try:
            if task['userId'] == _id:
                if task['completed']:
                    if len(task['title']) <= 48:
                        task_list.append(task['title'])
                    else:
                        task_list.append(f"{task['title'][0:48]}...")  # Добавление первых 48 символов и затем троеточия
        except KeyError:
            pass
    return task_list


def get_tasks_left(_id, tasks) -> list:
    """
    Функция получения списка невыполненных задач заданного пользователя
    :param _id: id проверяемого пользователя
    :param tasks: список словарей заданий пользователей
    :return: список оставшихся заданий проверяемого пользователя
    """
    task_list = []
    for task in tasks:
        try:
            if task['userId'] == _id:
                if not task['completed']:
                    if len(task['title']) <= 48:
                        task_list.append(task['title'])
                    else:
                        task_list.append(f"{task['title'][0:48]}...")  # Добавление первых 48 символов и затем троеточия
        except KeyError:
            pass
    return task_list


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

    tasks = get_info(TODOS_URL)
    text_field += f"Всего задач: {get_tasks_count(user['id'], tasks)}\n"  # Третья строка
    text_field += '\n'  # Четвертая строка
    completed_tasks_list = get_tasks_completed(user['id'], tasks)
    text_field += f"Завершенные задачи ({len(completed_tasks_list)}):\n"  # Пятая строка
    for completed_task in completed_tasks_list:
        text_field += f"{completed_task}\n"
    text_field += '\n'
    left_tasks_list = get_tasks_left(user['id'], tasks)
    text_field += f"Оставшиеся задачи ({len(left_tasks_list)}):\n"
    for left_task in left_tasks_list:
        text_field += f"{left_task}\n"

    new_file = open(f"{TASKS_PATH}{user['username']}.txt", 'w')
    new_file.write(text_field)
    new_file.close()


def rename_file(old_name) -> None:
    """
    Функция которая переименовывает исходный файл
    :param old_name: первоначальное имя файла (пользователя без txt)
    :return: None
    """
    old_path = f"{TASKS_PATH}{old_name}.txt"
    file = open(old_path, 'r')
    text = file.read()
    file.close()
    old_time = re.search(r"> (.*)\n", text).group(1)
    old_time = old_time.replace('.', '-')
    old_time = old_time.replace(' ', 'T')
    old_time = old_time.replace(':', '-')
    new_path = f"{TASKS_PATH}old_{old_name}_{old_time}.txt"
    os.rename(old_path, new_path)


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


def create_report() -> None:
    """
    Функция создания отчета
    :return:
    """
    users_list = get_info(USERS_URL)
    if create_dir():
        for user in users_list:
            create_file(user)
    else:
        print('Директория уже есть')
        for user in users_list:
            if os.path.exists(f"{TASKS_PATH}{user['username']}.txt"):
                rename_file(user['username'])


def main():
    create_report()


if __name__ == '__main__':
    main()
