#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import json
import math
import os
import shutil
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

MAX_RETRIES = 5
headers = {"Content-Type": "application/json;charset=utf-8",
           "Accept": "*/*",
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
           }

cards_data = []


def write_csv(file_name: str, row):
    with open(file_name, 'a', newline='\n', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL, delimiter=',')
        writer.writerow([row])


class DateTimeEncoder(json.JSONEncoder):
    """Класс для записи дат в JSON"""

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, bytes):
            return list(o)
        return json.JSONEncoder.default(self, o)


def add_all_to_json(data, file_name: str):
    with open(f'{file_name}', 'w', encoding='utf8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False, cls=DateTimeEncoder)


def add_to_json(file_name: str, card_data: dict = None):
    data = json.load(open(f'{file_name}', encoding='utf8')) if os.path.exists(
        f'{file_name}') else []
    data.append(card_data)
    with open(f'{file_name}', 'w', encoding='utf8', errors='ignore') as file:
        json.dump(data, file, indent=2, ensure_ascii=False, cls=DateTimeEncoder)  #


def unique(file_name: str):
    """Функция удаляющая дубли в переданном файле"""
    unique_lines = set(open(file_name, "r", encoding="utf-8").readlines())
    open(file_name, "w", encoding="utf-8").writelines(set(unique_lines))


def all_links(file_name: str, print_count: bool = False):
    """Функция возвращающая массив ссылок из файла"""
    with open(file_name, "r") as f:
        links = f.read().splitlines()

    if print_count:
        total_count = len(links)
        print(f"[INFO] Всего: {total_count}, последняя: {links[-1]}")

    return links


def set_session():
    """Функция установки соединения"""
    new_session = requests.Session()
    adapter = HTTPAdapter(max_retries=MAX_RETRIES)
    adapter.max_retries.respect_retry_after_header = False
    new_session.mount("https://", adapter)
    return new_session


def get_text(link: str) -> str:
    try:
        session = set_session()
        req = session.get(url=link, timeout=100, allow_redirects=True, headers=headers)
        if 200 <= req.status_code <= 299:
            time.sleep(0.5)
            return req.text.replace(u'\xa0', ' ').replace(u'\u202F', ' ')
        else:
            print(f'\r[WARNING]: ', f'{link} {req.status_code}', ' ', end='')
    except requests.exceptions.ReadTimeout:
        print('\n Подключение к серверу........ \n')
        time.sleep(5)


def links_count(link: str, card_in_page: int = 20, doctors: bool = False, doc_json: bool = False):
    try:
        session = set_session()
        if doc_json:
            url = 'https://api.doctu.ru/search/doctors?fullPath=/msk/doctors&path=/msk/doctors&query=%7B%7D'
            response = session.post(url=url, timeout=100, allow_redirects=True, headers=headers)
            if 200 <= response.status_code <= 299:
                json_data = response.json().get('result')
                return json_data.get('meta').get('lastPage') + 1
        else:
            req = session.get(url=link, timeout=100, allow_redirects=True, headers=headers)

            if 200 <= req.status_code <= 299:
                if doctors:
                    i = 2
                    while True:
                        next_page = f"{link}?page={i}"
                        req = session.get(url=next_page, timeout=100, allow_redirects=True, headers=headers)
                        if 200 <= req.status_code <= 299:
                            i += 1
                        else:
                            break
                    return i
                else:
                    soup = BeautifulSoup(req.text, 'lxml')
                    return math.ceil(int(soup.find('span', class_='green').text.strip()) / card_in_page) + 1
    except requests.exceptions.ReadTimeout:
        print('\n Подключение к серверу........ \n')
        time.sleep(5)


def split(path: str, file: str, divide: int = 1000):
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except FileExistsError as error:
            print(f'{path} > {error}')

    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except OSError as error:
            print(f'{path} > {error}')

    csv_file = open(file, 'r').readlines()
    filename = 1

    for i in range(len(csv_file)):
        if i % divide == 0:
            open(f'{path}links_{filename}.txt', 'w+').writelines(csv_file[i:i + divide])
            filename += 1
