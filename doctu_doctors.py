#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import multiprocessing
import re
from datetime import timedelta
from multiprocessing import Pool

from tqdm import tqdm
from utils import *


def doctors_links(link: str):
    response_text = get_text(link)
    soup = BeautifulSoup(response_text, "lxml")
    src = soup.find_all('div', class_=re.compile('doc-info'))
    for i in src:
        try:
            url = f"https://doctu.ru{i.find('div', class_='name').find('a').get('href')}"
        except:
            continue

        with open(f'doctu_doctors_links.txt', 'a') as file:
            file.write(url + '\n')


def get_doctors_info(link: str):
    response_text = get_text(link)
    soup = BeautifulSoup(response_text, "lxml")

    try:
        block = soup.find('div', class_=re.compile('doc-name'))
        name = block.find('h1').text.strip()
        experience = block.find('div', class_='experience').text.strip().replace(u'\xa0', ' ').replace(u'\u202F', ' ')
        city = block.find('div', class_='note').text.strip()
    except:
        name = ''
        city = ''
        experience = ''

    try:
        specialty = soup.find('div', class_=re.compile('doc-name')).find('div', class_=re.compile(
            'specialty')).text.strip()
    except:
        specialty = ''

    try:
        intro = soup.find('p', class_=re.compile('doc-intro')).text.strip().replace(u'\xa0', ' ').replace(u'\u202F',
                                                                                                          ' ')
    except:
        intro = ''

    try:
        block1 = soup.find('div', class_=re.compile('col-xs-4 education'))
        education = [b.getText().strip().replace(u'\xa0', ' ').replace(u'\u202F', ' ').replace('\n', ' - ') for b in
                     block1.find_all('div', class_=re.compile("school$"))]
        training = [b.getText().replace(u'\xa0', ' ').replace(u'\u202F', ' ').replace('\n', ' ').strip() for b in
                    block1.find_all('div', class_='training')]
        work = [b.getText().strip().replace(u'\xa0', ' ').replace(u'\u202F', ' ').replace('\n', ' - ') for b in
                block1.find_all('div', class_='school work')]
        education = [x for x in education if x not in work]
    except:
        education = []
        work = []
        training = []

    try:
        block2 = soup.find('div', class_=re.compile('col-xs-8 right_review'))
        skills = block2.find('ul').text.replace('.', '').replace(u'\xa0', ' ').replace(u'\u202F', ' ').split(',')
        address = [re.sub('\n+', '\n', ' * '.join(
            b.text.replace(u'\xa0', ' ').replace(u'\u202F', ' ').strip().split('\n\n\n\n\n\n\n'))).split(' * ') for b in
                   block2.find_all('section', class_='doc-address clearfix')][0]
        address = address[0: len(address) - 1]
        reviews = [re.sub('\n+', '\n', ' * '.join(
            b.text.replace(u'\xa0', ' ').replace(u'\u202F', ' ').strip().split('\n\n\n\n\n\n\n'))).split(' * ') for b in
                   block2.find_all('section', class_='reviews-list')][0]
        reviews = re.sub('\n | \n', '\n', re.sub('г.\n\d+', 'г.', re.sub(' +', ' ',
                                                                         ' * '.join(reviews).replace('\nПациент',
                                                                                                     'Пациент')))).split(
            ' * ')
    except:
        skills = []
        address = []
        reviews = []

    data = {'link': link,
            'name': name,
            'experience': experience,
            'city': city,
            'specialty': specialty,
            'intro': intro.replace(u'\xa0', ' ').replace(u'\u202F', ' '),
            'education': education,
            'training': training,
            'work': work,
            'skills': skills,
            'address': address,
            'reviews': reviews, }

    return data


def multiprocess(link: str):
    data = get_doctors_info(link)
    print(f'\r[INFO] Done: ', link, ' ', end='')
    return data


def doctors(get_links: bool = False):
    print('Начали: %s' % time.ctime())
    start_time = time.monotonic()

    if get_links:
        print(f'\r[INFO] Получаем количество ссылок...')
        count = links_count('https://doctu.ru/msk/doctors', doctors=True)
        for i in tqdm(range(1, count, 1)):
            link = f'https://doctu.ru/msk/doctors?page={i}'
            doctors_links(link)

    doctor_links = all_links(f'doctu_doctors_links.txt', True)
    with Pool(multiprocessing.cpu_count()) as p:
        for result in p.map(multiprocess, doctor_links):
            cards_data.append(result)

    add_all_to_json(cards_data, f'doctu_doctors_info.json')

    print('')
    print('Закончили: %s' % time.ctime())
    print('Общее время: %s' % timedelta(seconds=time.monotonic() - start_time))


if __name__ == "__main__":
    doctors(False)
