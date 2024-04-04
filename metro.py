import sqlite3
import json
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

url = "https://metro.zakaz.ua/uk/promotions/"
classes = {
    'item': 'ProductsBox__listItem',
    'more_items_button': 'Button Button_primary Button_large',
    'name': 'ProductTile__title',
    'photo': 'ProductTile__image',
    'price': 'Price__value_discount',
    'unit': 'ProductTile__weight',
    'old_price': 'Price__value_minor'
}

db_name = 'goods.db'
json_name = 'results.json'

driver = webdriver.Chrome()
driver.get(url)

def close_modal():
    close_modal_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'CustomModalHeader__closeButton'))
    )
    close_modal_button.click()

close_modal()

while True:
    try:
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="PageWrapBody_desktopMode"]/div/div[4]/button'))
        )
        driver.execute_script("arguments[0].click();", button)
    except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
        break

page_source = driver.page_source
driver.quit()

soup = BeautifulSoup(page_source, "html.parser")
sys.stdout.reconfigure(encoding='utf-8')

items = soup.find_all('div', class_= classes['item'])
dictionary = []

con = sqlite3.connect(db_name)
cursor = con.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS goods (name TEXT, photo TEXT, price REAL, unit TEXT, old_price REAL)''')
SQL = '''INSERT INTO goods (name, photo, price, unit, old_price) VALUES (?,?,?,?,?)'''

for i in range(0, len(items)):
    name = items[i].find('span', class_ = classes['name'])
    photo = items[i].find('img', class_ = classes['photo'])
    price = items[i].find('span', class_ = classes['price'])
    unit = items[i].find('div', class_ = classes['unit'])
    old_price = items[i].find('span', class_ = classes['old_price'])

    item = {
        'name': name.text,
        'photo': photo['src'],
        'price': float(price.text),
        'unit': unit.text if unit else 'шт',
        'old_price': float(old_price.text)
    }

    cursor.execute(SQL, (item['name'], item['photo'], item['price'], item['unit'], item['old_price']))
    dictionary.append(item)

con.commit()
con.close()

with open(json_name, 'w', encoding='utf-8') as file:
    json.dump(dictionary, file, ensure_ascii=False)