#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import math
import os
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
            return req.text.replace(u'\xa0', ' ').replace(u'\u202F', ' ')
    except requests.exceptions.ReadTimeout:
        print('\n Подключение к серверу........ \n')
        time.sleep(5)


def links_count(link: str, card_in_page: int = 20, doctors: bool = False):
    try:
        session = set_session()
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
