import requests
from pprint import pprint
import os
from datetime import datetime
import re


USERS_URL = 'https://json.medrating.org/users'
TODOS_URL = 'https://json.medrating.org/todos'
BASE_PATH = os.getcwd()
TASKS_PATH = BASE_PATH + '\\tasks\\'


def get_info(url):
    list = requests.get(url).json()
    return list


def get_tasks_count(id, tasks):
    count = 0
    for task in tasks:
        try:
            if task['userId'] == id:
                count += 1
        except KeyError:
            pass
    return count


def get_tasks_completed(id, tasks) -> list:
    task_list = []
    for task in tasks:
        try:
            if task['userId'] == id:
                if task['completed']:
                    if len(task['title']) <= 48:
                        task_list.append(task['title'])
                    else:
                        task_list.append(f"{task['title'][0:48]}...")  # Добавление первых 48 символов и затем троеточия
        except KeyError:
            pass
    return task_list


def get_tasks_left(id, tasks) -> list:
    task_list = []
    for task in tasks:
        try:
            if task['userId'] == id:
                if not task['completed']:
                    if len(task['title']) <= 48:
                        task_list.append(task['title'])
                    else:
                        task_list.append(f"{task['title'][0:48]}...")  # Добавление первых 48 символов и затем троеточия
        except KeyError:
            pass
    return task_list


def create_file(user):
    text_field = ''  # Формирование содержимого файла
    text_field += f"Отчет для {user['company']['name']}.\n"  # Первая строка
    text_field += f"{user['name']} < {user['email']}> "  # Вторая строка

    current_date = datetime.now()
    date_fixed = f"{current_date.day}.{current_date.month}.{current_date.year} {current_date.hour}:{current_date.minute}"  # поменять

    text_field += f"{date_fixed}\n"  # Добавление даты в нужном формате

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


def rename_file(old_name):
    old_path = f"{TASKS_PATH}{old_name}.txt"
    # old_path = os.path.join(TASKS_PATH, )
    file = open(old_path, 'r')
    text = file.read()
    file.close()
    old_time = re.search(r"> (.*)\n", text).group(1)
    old_time = old_time.replace('.', '-')
    old_time = old_time.replace(' ', 'T')
    old_time = old_time.replace(':', '-')
    new_path = f"{TASKS_PATH}old_{old_name}_{old_time}.txt"
    os.rename(old_path, new_path)


def create_dir():
    try:
        os.mkdir(TASKS_PATH)
    except OSError:
        return False
    else:
        return True


def create_report():
    # if create_dir():
    users_list = get_info(USERS_URL)
    for user in users_list:
        if not os.path.exists(os.path.join(TASKS_PATH, f"{user['username']}.txt")):
            create_file(user)
        else:
            rename_file(user['username'])
    # else:
    #     print('Директория уже есть')


create_report()
