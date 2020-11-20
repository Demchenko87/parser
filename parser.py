import requests
import csv
import subprocess

from bs4 import BeautifulSoup
URL = 'https://auto.ria.com/newauto/marka-lexus/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:83.0) Gecko/20100101 Firefox/83.0', 'accept': '*/*'}
HOST = 'https://auto.ria.com'
FILE = 'cars.csv'
def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r
def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('span', class_='page-item mhide')
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1
def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='proposition')
    cars = []
    for item in items:
        uah_price = item.find('span', class_='grey size13')
        if uah_price:
            uah_price = uah_price.get_text() # .replace(' * ', '')
        else:
            uah_price = 'Цены в грн нет'
        cars.append({
            'title': item.find('h3', class_='proposition_name').get_text(strip=True),
            'link': HOST + item.find('a').get('href'),
            'usd_price': item.find('span', class_='green').get_text(strip=True),
            'uah_price': uah_price,
            'city': item.find('div', class_='proposition_region').find_next('strong').get_text(strip=True),
        })
    return cars
def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Марка', 'Ссылка', 'Цена в $', 'Цена в грн.', 'Город'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['usd_price'], item['uah_price'], item['city']])
def parse():
    URL = input('Ведите URL: ')
    URL = URL.strip()
    html = get_html(URL)
    if html.status_code == 200:
        cars = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} из {pages_count}...')
            html = get_html(URL, params={'page': page})
            cars.extend(get_content(html.text))
        save_file(cars, FILE)
        print(f'Получено {len(cars)} автомобилей')
        subprocess.run(['open', FILE], check=True)
    else:
        print('Error')
parse()
