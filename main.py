import json
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient

url = 'https://www.parsemachine.com/sandbox/catalog/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 OPR/99.0.0.0 (Edition Yx GX)'
}

# Скачиваем HTML-код страницы
req = requests.get(url, headers=headers)
src = req.text

# Сохраняем HTML-код в файл
with open('parser.html', 'w', encoding='utf-8') as f:
    f.write(req.text)

# Читаем HTML-код из файла
with open('parser.html', encoding='utf-8') as f:
    src = f.read()

# Парсим HTML-код с помощью BeautifulSoup
soup = BeautifulSoup(src, 'lxml')
cards = soup.find_all('div', class_="col-xl-3 col-lg-3 col-md-4 col-sm-6 col-6 mb-3")

card_urls = []
for card in cards:
    card_url = 'https://www.parsemachine.com' + card.find('div', class_='card product-card').find('a').get('href')
    card_urls.append(card_url)

card_data = []
for card_url in card_urls:
    req = requests.get(card_url, headers)
    card_name = card_url.split('/')[-2]

    with open(f'data/{card_name}.html', 'w', encoding='utf-8') as f:
        f.write(req.text)

    with open(f'data/{card_name}.html', encoding='utf-8') as f:
        src = f.read()

    soup = BeautifulSoup(src, 'lxml')
    card_data_row = soup.find('div', class_='row py-2 py-md-3')

    try:
        card_logo = 'https://www.parsemachine.com' + soup.find('div', class_='preview').find('img').get('src')
    except Exception:
        card_logo = "Логотип не найден"

    try:
        card_name = card_data_row.find('div', class_='col-12').find('h1').text.strip()
    except Exception:
        card_name = 'Имя не найдено'

    try:
        card_info = card_data_row.find('div', class_='col-12').find('p', class_='mt-4 mb-2').find('span', id='description').text.replace('\n', '').strip()
    except Exception:
        card_info = 'Информация не найдена'

    try:
        card_price = card_data_row.find('div', class_='col-lg-7 col-sm-7 col-12').find('div', class_='row').find('p', class_='mt-0 mb-0')\
        .find('big').text
    except Exception:
        card_price = 'Цена не найдена'

    try:
        card_characters = card_data_row.find('div', class_='col-xl-6 col-lg-7 col-md-8 col-sm-7 col-12').find('div', 'table-responsive')\
        .find('table', 'table table-hover mb-2').find('tr').find_all_next('td')
        values = [td.text.strip() for td in card_characters[1::2]]
        width= values[0]
        height = values[1]
        depth = values[2]
    except Exception:
        width = 'Характеристика не найдена'
        height = 'Характеристика не найдена'
        depth = 'Характеристика не найдена'

    card_data.append(
        {
        "card_logo": card_logo,
        "card_name": card_name,
        "width": width,
        "height": height,
        "depth": depth,
        "card_price": card_price,
        })

# Сохраняем данные в JSON-файл
with open('card_data.json', 'w', encoding='utf-8') as f:
    json.dump(card_data, f, ensure_ascii=False, indent=4)

# Подключаемся к MongoDB
client = MongoClient('mongodb://localhost:27017')
# Создаем базу данных 'parser'
db = client['parser']

# Создаем коллекцию 'parser'
collection = db['parser']

with open('card_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Добавляем данные в коллекцию MongoDB
collection.insert_many(data)
