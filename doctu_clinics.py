#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import multiprocessing
import re
from datetime import timedelta
from multiprocessing import Pool

from tqdm import tqdm
from utils import *


def clinics_links(link: str):
    response_text = get_text(link)
    soup = BeautifulSoup(response_text, "lxml")
    src = soup.find_all('div', class_=re.compile('clinic-description'))

    for i in src:
        try:
            url = f"https://doctu.ru{i.find('div', class_='name').find('a').get('href')}"
        except:
            continue

        with open(f'doctu_clinics_links.txt', 'a') as file:
            file.write(url + '\n')


def doctors_info(link: str):
    response_text = get_text(link)
    soup = BeautifulSoup(response_text, "lxml")

    try:
        doctors = soup.find_all('section', class_=re.compile('doctor_2_0'))
        result = []
        for item in doctors:
            name = item.find('div', class_=re.compile('name')).text.strip().replace('\n', ' ')
            price = item.find('div', class_=re.compile('price-label')).text.strip() if item.find('div',
                                                                                                 class_=re.compile(
                                                                                                     'price-label')) else ''
            result.append(f"{name} "
                          f"({item.find('div', class_=re.compile('speciality')).text.strip()}) "
                          f"{item.find('div', class_=re.compile('rating')).text.strip()} "
                          f"{price}".strip().replace(u'\xa0', ' ').replace(u'\u202F', ' '))
        return result
    except:
        pass


def services_info(link: str):
    response_text = get_text(link)
    soup = BeautifulSoup(response_text, "lxml")

    try:
        services = soup.find_all(class_=re.compile('service-link'))
        result = []
        for item in services:
            name = item.find('span', itemprop=re.compile('name')).text.strip().replace('\n', ' ')
            if len(item.find(class_=re.compile('pull-right price')).getText().strip()):
                price = item.find(class_=re.compile('pull-right price')).getText().strip()
            else:
                price = 'по запросу'
            # result.append(f"{name} {price}".replace(u'\xa0', ' ').replace(u'\u202F', ' '))
            result.append({
                "name": name.replace(u'\xa0', ' ').replace(u'\u202F', ' '),
                "price": price.replace(u'\xa0', ' ').replace(u'\u202F', ' ')
            })
        return result
    except:
        pass


def reviews_info(link: str):
    response_text = get_text(link)
    soup = BeautifulSoup(response_text, "lxml")

    try:
        reviews = soup.find('section', class_='reviews-list').find_all('div',
                                                                       class_=re.compile(
                                                                           'rev-item clinics-review'))
        result = []
        for item in reviews:
            review = []
            for el in item.find_all('div', class_=re.compile('rev-text')):
                review.append(el.text.strip().replace('\n', ' '))
            review = "\n".join(review)
            rating = item.find('span', class_=re.compile('rating-val')).text.strip().replace('.', ',')
            date = item.find('div', class_=re.compile('rev-date')).text.strip()
            result.append(f"{date} {rating}\n{review}".replace(u'\xa0', ' ').replace(u'\u202F', ' '))
        return result
    except:
        pass


def get_clinic_info(link: str):
    response_text = get_text(link)
    try:
        soup = BeautifulSoup(response_text, "lxml")

        try:
            name = ' '.join(soup.find('h1', itemprop=re.compile('name')).text.strip().split(' ')[:-2]).strip()
        except:
            name = ''

        try:
            city = soup.find('h1', itemprop=re.compile('name')).text.strip().split(' ')[-1]
            street = soup.find('span', itemprop=re.compile('streetAddress')).text.strip()
            if city == 'Москва':
                address = f"{city} {street}"
            else:
                address = f"{street}"
        except:
            address = ''

        try:
            metro = re.sub('\n+', '\n', soup.find('div', class_=re.compile('metro')).text.strip()).split('\n')
        except:
            metro = []

        try:
            about = re.sub('\n+', '\n', soup.find('div', class_=re.compile('col-xs-8')).text.strip()).replace(
                '            ', ' ').replace(u'\xa0', ' ').replace(u'\u202F', ' ').replace('\'', '\"')
        except:
            about = ''

        try:
            telephone = soup.find('div', class_=re.compile('clinic-contacts')).text.strip()
        except:
            telephone = ''

        try:
            rating = float(soup.find('div', itemprop=re.compile('rating')).text.strip())
        except:
            rating = 0

        try:
            category_main = soup.find('ol', class_=re.compile('breadcrumb')).find_all('li')[-2].text.strip()
        except:
            category_main = ''

        try:
            left_block = soup.find('div', class_=re.compile('col-xs-4 col-left-border')) \
                .find_all('div', class_='additional-info-block')

            category_all = chief_physician = schedule = None
            for item in left_block:
                text = item.text.strip()
                if text.find('Категория') != -1:
                    category_all = text.split('Категория')[-1].strip()
                elif text.find('Главный врач') != -1:
                    chief_physician = text.split('Главный врач')[-1].strip()
                elif text.find('пн-пт') != -1 or text.find('круглосуточно') != -1:
                    schedule = text.replace('\n', ' ').split('   ')
        except:
            category_all = ''
            chief_physician = ''
            schedule = []

        try:
            licenses_link = soup.find_all('div', class_='licenceImg')
            licenses = [f"https://doctu.ru{p.find('a').get('href')}" for p in licenses_link]
        except:
            licenses = []

        try:
            avatar = f"https://doctu.ru{soup.find('div', class_='clinic-avatar').find('img').get('src')}"
        except:
            avatar = ''

        try:
            photo = soup.find('div', class_='row row-photo').find_all('div', class_='col-xs-2 galleryImg')
            clinic_photo = [f"https://doctu.ru{p.find('a').get('href')}" for p in photo]

        except:
            clinic_photo = []

        try:
            site = f"https://doctu.ru{soup.find('a', class_=re.compile('btn btn-primary site')).get('href')}"
        except:
            site = ''

        try:
            vk = youtube = None
            network_links = soup.find_all('a', class_=re.compile('spec-link site'))
            for item in network_links:
                item = item.get('href')
                if item.split('/')[-1] == 'vk':
                    vk = f"https://doctu.ru{item}"
                elif item.split('/')[-1] == 'youtube':
                    youtube = f"https://doctu.ru{item}"
        except:
            vk = ''
            youtube = ''

        doctors = services = reviews = None
        for item in soup.find('ul', class_=re.compile('nav nav-tabs')).find_all('li'):
            nav_link = item.find('a').get('href')
            if nav_link and nav_link.split("/")[-1] == "doctors":
                try:
                    doctors = doctors_info(f"https://doctu.ru{nav_link}")
                except:
                    doctors = []
            elif nav_link and nav_link.split("/")[-1] == "services":
                try:
                    services = services_info(f"https://doctu.ru{nav_link}")
                except:
                    services = []
            elif nav_link and nav_link.split("/")[-1] == "reviews":
                try:
                    reviews = reviews_info(f"https://doctu.ru{nav_link}")
                except:
                    reviews = []

        data = {'link': link,
                'name': name,
                'address': address,
                'metro': metro,
                'telephone': telephone,
                'about': about,
                'schedule': schedule,
                'rating': rating,
                'category_main': category_main,
                'category_all': category_all,
                'licenses': licenses,
                'avatar': avatar,
                'clinic_photo': clinic_photo,
                'chief_physician': chief_physician,
                'site': site,
                'vk': vk,
                'youtube': youtube,
                'doctors': doctors,
                'services': services,
                'reviews': reviews,
                }

        return data
    except:
        print(response_text)
        pass


def multiprocess(link: str):
    data = get_clinic_info(link)
    print(f'\r[INFO] Done: ', link, ' ', end='')
    return data


def clinic(get_links: bool = False):
    print('Начали: %s' % time.ctime())
    start_time = time.monotonic()

    if get_links:
        print(f'\r[INFO] Получаем количество ссылок...')
        clinic_links_count = links_count('https://doctu.ru/msk/clinics')
        for i in tqdm(range(1, clinic_links_count, 1)):
            link = f'https://doctu.ru/msk/clinics?page={i}'
            clinics_links(link)

    clinic_links = all_links(f'doctu_clinics_links.txt', True)
    with Pool(multiprocessing.cpu_count()) as p:
        for result in p.map(multiprocess, clinic_links):
            cards_data.append(result)

    add_all_to_json(cards_data, f'doctu_clinic_info.json')

    print('')
    print('Закончили: %s' % time.ctime())
    print('Общее время: %s' % timedelta(seconds=time.monotonic() - start_time))


if __name__ == "__main__":
    clinic(True)
