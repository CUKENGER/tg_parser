import aiohttp
import asyncio
from bs4 import BeautifulSoup

from database.sqlite_db import Database
import config as cfg
from create_kwork import bot

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


url = 'https://kwork.ru/projects?c=41&attr=3587'

def scroll_to_bottom(driver):
	body = driver.find_element(By.XPATH, '//body')
	body.send_keys(Keys.END)
	time.sleep(3)
	wait = WebDriverWait(driver, 10)

async def get_data(driver, url_, page, tgid):
    db = Database(cfg.path_to_db)

    _url = f'{url_}&page={page}'

    driver.get(_url)

    async with aiohttp.ClientSession() as session:
        response = await session.get(_url)

        await response.text()

        # await asyncio.sleep(2)

        soup = BeautifulSoup(await response.text(), 'lxml')
        # data = soup.find_all('div', class_='wants-card__header-title first-letter breakwords pr250')
        data_list = driver.find_elements(By.CLASS_NAME, 'wants-card__header-title')
        kwork_names = []
        for i in data_list:
            print(f'data : {i.text}')

            link = i.find_element(By.TAG_NAME, 'a').get_attribute('href')
            name = i.text
            print(f'name: {name}')
            print(f'link: {link}')

            if name not in kwork_names:
                mes_text = '<b>Уведомление 🔔</b>' \
                        f'<a href="{link}">Появился новый заказ!</a>\n' \

                await bot.send_message(tgid, mes_text, parse_mode='HTML')
                await db.add_kwork(name)

        
        for ii in await db.get_kwork_names():
            kwork_names.append(ii[0])


async def get_page(driver, tgid):
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)

        await response.text()

        soup = BeautifulSoup(await response.text(), 'lxml')

        driver.get(url)
        wait = WebDriverWait(driver, 5)
        element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card")))
        scroll_to_bottom(driver)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'paging'))
        )

        # print('Respinse:', await response.text())
        # count_page = soup.find('div', class_='paging').find_all('a')[-2].text
        pages = driver.find_elements(By.CLASS_NAME, 'mr4')
        active_page = driver.find_element(By.XPATH, '//*[@class="active"]/')
        page = pages.index(active_page) 

        if page + 1 < len(pages):
            next_page = pages[page + 1]
            page = next_page
        else:
            print('Это последняя страница')

        await get_data(driver, url, page, tgid )
        # count_page = driver.find_element(By.CLASS_NAME, 'paging').find_elements(By.TAG_NAME, 'a')[-2].text
        # print(f'count_page: \n{count_page}')

        from selenium.webdriver.common.by import By

        # Находим элемент с классом 'active'
        active_element = driver.find_element(By.CSS_SELECTOR, 'a.active')

        # Находим родительский элемент 'li' для активного элемента
        active_li = active_element.find_element(By.XPATH, '..')

        # Находим все элементы 'li'
        li_elements = driver.find_elements(By.TAG_NAME, 'li')

        # Находим индекс активного элемента 'li' в списке всех элементов 'li'
        active_index = li_elements.index(active_li)

        # Проверяем, есть ли следующий элемент 'li'
        if active_index + 1 < len(li_elements):
            # Если есть, переходим к следующему элементу 'li'
            next_li = li_elements[active_index + 1]
        else:
            print("Это последний элемент 'li'.")


    # for page in range(1, int(count_page) + 1):
    #     await get_data(driver, url, page, tgid)



async def start_pars(tgid):
    db = Database(cfg.path_to_db)
    status = db.get_status_user(tgid)
    print(status)
    if status[0] == 'active':
        options = Options()
        options.add_argument('--headless')
        options.add_argument('log-level=3')
        driver = webdriver.Chrome(options=options)

        try:
            await get_page(driver, tgid)
        finally:
            driver.quit()
    else:
        print('Парсинг невозможен')












