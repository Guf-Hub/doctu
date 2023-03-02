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
    except:
        block = None

    if block:
        try:
            name = block.find('h1').text.strip()
        except:
            name = ''

        try:
            city = block.find('div', class_='note').text.strip()
        except:
            city = ''

        try:
            experience = block.find('div', class_='experience').text.strip().replace(u'\xa0', ' ').replace(u'\u202F',
                                                                                                           ' ')
        except:
            experience = ''

        try:
            specialty = block.find('div', class_=re.compile('specialty')).text.strip()
        except:
            specialty = ''

        try:
            intro = soup.find('p', class_=re.compile('doc-intro')).text.strip().replace(u'\xa0', ' ').replace(u'\u202F',
                                                                                                              ' ')
        except:
            intro = ''

        try:
            block1 = soup.find('div', class_=re.compile('col-xs-4 education'))
        except:
            block1 = None

        education = work = training = None
        if block1:
            try:
                education = [b.getText().strip().replace(u'\xa0', ' ').replace(u'\u202F', ' ').replace('\n', ' - ') for
                             b in
                             block1.find_all('div', class_=re.compile("school$"))]
                work = [b.getText().strip().replace(u'\xa0', ' ').replace(u'\u202F', ' ').replace('\n', ' - ') for b in
                        block1.find_all('div', class_='school work')]
                education = [x for x in education if x not in work]
            except:
                education = []
                work = []

            try:
                training = [b.getText().replace(u'\xa0', ' ').replace(u'\u202F', ' ').replace('\n', ' ').strip() for b
                            in
                            block1.find_all('div', class_='training')]
            except:
                training = []

        try:
            block2 = soup.find('div', class_=re.compile('col-xs-8 right_review'))
        except:
            block2 = None

        skills = address = reviews = None
        if block2:
            try:
                # skills = [f'{item}\n'.join(
                #     [i.text.replace(u'\xa0', ' ').replace(u'\u202F', ' ').replace(';', '.').capitalize() for i in
                #      block2.findAll('li')]) for item in block2.findAll('ul')]
                skills = [i.text.replace(u'\xa0', ' ').replace(u'\u202F', ' ').replace(';', '.').capitalize() for i in block2.findAll('li')]
            except:
                skills = []

            try:
                address = [re.sub('\n+', '\n', ' * '.join(
                    b.text.replace(u'\xa0', ' ').replace(u'\u202F', ' ').strip().split('\n\n\n\n\n\n\n'))).split(' * ')
                           for
                           b in block2.find_all('section', class_='doc-address clearfix')][0]
                address = address[0: len(address) - 1]
            except:
                address = []

            try:
                reviews = [re.sub('\n+', '\n', ' * '.join(
                    b.text.replace(u'\xa0', ' ').replace(u'\u202F', ' ').strip().split('\n\n\n\n\n\n\n'))).split(' * ')
                           for
                           b in block2.find_all('section', class_='reviews-list')][0]
                reviews = re.sub('\n | \n', '\n', re.sub('г.\n\d+', 'г.', re.sub(' +', ' ',
                                                                                 ' * '.join(reviews).replace(
                                                                                     '\nПациент',
                                                                                     'Пациент')))).split(
                    ' * ')
            except:
                reviews = []

        data = {'link': link,
                'name': name,
                'experience': experience,
                'city': city,
                'specialty': specialty,
                'intro': intro,
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
