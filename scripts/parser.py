import os.path
import re
import sqlite3

import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By

from time import sleep
from datetime import datetime
import urllib.request
import emoji

red_mark = ":red_circle:"
yellow_mark = ":yellow_circle:"
green_mark = ":green_circle:"
blue_mark = ":blue_circle:"
white_mark = ":white_circle:"
emoji_mapping = {
    "выше": "- Выше рынка :red_circle:",
    "соответствует Авито Оценке": "- Рыночная :white_circle:",
    "ниже": "- Ниже рынка :green_circle:"
}

show_print = True
print = print if show_print else str

options = webdriver.ChromeOptions()

options.add_argument('--disable-extensions')
options.add_argument('ignore-certificate-errors')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('disable-infobars')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-setuid-sandbox')
options.add_argument('--no-zygote')

browser = webdriver.Chrome(chrome_options=options)
browser.set_page_load_timeout(30)

def parsing():
    while True:
        for user in sqlite3_query("SELECT id, name, message, count_ads, search_status, search_link FROM user"):
            try:
                if not os.path.exists(fr"data\log_data/{user[0]}.ini"):
                    with open(fr"data\log_data/{user[0]}.ini", "w", encoding='utf-8-sig') as file:
                        file.write('\n')

                with open(fr"data\log_data/{user[0]}.ini", encoding='utf-8-sig') as file:
                    file = file.readlines()
                if len(file) >= 100:
                    with open(fr"data\log_data/{user[0]}.ini", "w", encoding='utf-8-sig') as second_file:
                        second_file.writelines(file[-40:])

                print(f"[{emoji.emojize(green_mark)}]LOG|[{datetime.now().time().replace(microsecond=0)}]|ID:{user[0]}|{user[1]}| Try find.")
                if user[4] == 1:
                    browser.get(user[5])
                    check_button(user)
                    index_link, carlink = check_skiped_ads(user)
                    parsing_infomation(index_link, carlink, user)
                else:
                    print(f"[{emoji.emojize(white_mark)}]LOG|[{datetime.now().time().replace(microsecond=0)}]|ID:{user[0]}|{user[1]}| Status OFF")
                    sleep(0.2)
            except Exception as e:
                print(f"[{emoji.emojize(red_mark)}]LOG|[{datetime.now().time().replace(microsecond=0)}]|ID:{user[0]}|{user[1]}| Error")
                sleep(1.5)

def check_button(user):
    try:
        try:
            browser.find_element(By.XPATH,"//label[@class='filters-filter-_Hhcm checkbox-checkbox-KO_ws checkbox-size-s-tYC2A checkbox-checked-_eGx7 checkbox-set-W_iAg']")
        except Exception as e:
            browser.find_element(By.XPATH, "//div[@class='main-richTitleWrapper__content-WLi_V']").click()
            sleep(1.5)
            try:
                button = browser.find_element(By.XPATH, "//span[text()='Сначала в выбранном регионе']")
            except Exception as e:
                button = browser.find_element(By.XPATH, "//span[text()='Сначала в выбранном радиусе']")
            browser.execute_script("arguments[0].click();", button)
            sleep(1.5)
            browser.find_element(By.XPATH,"//button[@class='button-button-CmK9a button-size-m-LzYrF button-primary-x_x8w']").click()
            print(f"[{emoji.emojize(yellow_mark)}]LOG|[{datetime.now().time().replace(microsecond=0)}]|ID:{user[0]}|{user[1]}| Only this region button pressed")
            sleep(1.5)
    except Exception as e:
        print(f"[{emoji.emojize(red_mark)}]LOG|[{datetime.now().time().replace(microsecond=0)}]| Error in check_button {e}")
        sleep(10)

def check_skiped_ads(user):
    try:
        index_link = 0
        carlink = browser.find_element(By.XPATH,f"//div[@data-marker='item'][{index_link+1}]//a[@class='iva-item-sliderLink-uLz1v']").get_attribute('href')
        if not f"{carlink}\n" in open(fr"data\log_data/{user[0]}.ini", encoding='utf-8-sig').readlines():
            findstatus = True
            while findstatus:
                carlink = browser.find_element(By.XPATH,f"//div[@data-marker='item'][{index_link+1}]//a[@class='iva-item-sliderLink-uLz1v']").get_attribute('href')
                if not f"{carlink}\n" in open(fr"data\log_data/{user[0]}.ini", encoding='utf-8-sig').readlines()[-1]:
                    if index_link >= 3:
                        carlink = browser.find_element(By.XPATH,f"//div[@data-marker='item'][{index_link+1}]//a[@class='iva-item-sliderLink-uLz1v']").get_attribute('href')
                        findstatus = False
                        print(f"[{emoji.emojize(yellow_mark)}]LOG|[{datetime.now().time().replace(microsecond=0)}]|ID:{user[0]}|{user[1]}| Index more limit")
                    else:
                        index_link += 1
                        print(f"[{emoji.emojize(green_mark)}]LOG|[{datetime.now().time().replace(microsecond=0)}]|ID:{user[0]}|{user[1]}| Plus index - {index_link}")
                elif f"{carlink}\n" in open(fr"data\log_data/{user[0]}.ini", encoding='utf-8-sig').readlines()[-1]:#
                    index_link -= 1
                    carlink = browser.find_element(By.XPATH,f"//div[@data-marker='item'][{index_link+1}]//a[@class='iva-item-sliderLink-uLz1v']").get_attribute('href')
                    findstatus = False
                    print(f"[{emoji.emojize(green_mark)}]LOG|[{datetime.now().time().replace(microsecond=0)}]|ID:{user[0]}|{user[1]}| Find old ad")
        return index_link, carlink
    except Exception as e:
        print(f"[{emoji.emojize(red_mark)}]LOG|[{datetime.now().time().replace(microsecond=0)}]| Error in check_skip")

def parsing_infomation(index_link, carlink, user):
    try:
        with open(fr"data\log_data/{user[0]}.ini", "r+", encoding='utf-8-sig') as file:
            file_read = file.readlines()
            if not carlink+"\n" in file_read[-1] and carlink+"\n" in file_read:
                file.write(carlink+"\n")

        try:
            upped_status = ":up_arrow: Объявление продвинуто! :up_arrow:~"
            browser.find_element(By.XPATH,f"//div[@data-marker='item'][{index_link + 1}]//div[@class='styles-arrow-jfRdd']")
        except Exception as e:
            upped_status = ""

        if not carlink+"\n" in file_read:
            carname = browser.find_element(By.XPATH,f"//div[@data-marker='item'][{index_link+1}]//div[@class='iva-item-titleStep-pdebR']").text
            cardescription = browser.find_element(By.XPATH,f"//div[@data-marker='item'][{index_link+1}]//div[@class='iva-item-autoParamsStep-WzfS8']").text
            carfulldescription = browser.find_element(By.XPATH,f"//div[@data-marker='item'][{index_link+1}]//div[@class='iva-item-descriptionStep-C0ty1']").text
            cartime = browser.find_element(By.XPATH,f"//div[@data-marker='item'][{index_link+1}]//div[@class='iva-item-dateInfoStep-_acjp']").text
            browser.get(carlink)
            linkphoto = browser.find_element(By.XPATH, "//div[@class='image-frame-wrapper-_NvbY']/img").get_attribute('src')
            try:
                carcost = browser.find_element(By.XPATH, "//span[@class='desktop-ged5cz']").text
                for key, value in emoji_mapping.items():
                    if key in carcost:
                        carcost = carcost.split("— ")
                        carcost = carcost[0] + value
                        break
            except Exception as e:
                carcost = browser.find_element(By.XPATH,"//span[@class='js-item-price style-item-price-text-_w822 text-text-LurtD text-size-xxl-UPhmI']").text + " ₽"
            try:
                moderationstatus = ":double_exclamation_mark:*" + browser.find_element(By.XPATH,"//span[@class='text-text-LurtD text-size-s-BxGpL text-bold-SinUO']").text + "*:double_exclamation_mark:" + "~"
            except Exception as e:
                moderationstatus = ""
            if user[4] == 1:
                if len(carfulldescription) > 150:
                    carfulldescription = f"{re.findall('(.{100}|.+$)', carfulldescription)[0]}..."
                carfulldescription = emoji.demojize(carfulldescription)
                print(f"[{emoji.emojize(green_mark)}]LOG|[{datetime.now().time().replace(microsecond=0)}]| NEW CAR For [{user[0]}] [{user[1]}]\nНазвание: {carname}\nЦена: {carcost}\nОписание: {cardescription}\nПолное описание: {carfulldescription}\nВышел: {cartime}\nСсылка: {carlink}")
                carinfo = f"{upped_status}{moderationstatus}*Название*: {carname}~*Цена*: {carcost}~*Вышел*: {cartime}~*Описание*: {cardescription}~*Полное описание*: {carfulldescription}&{carlink}"
                carinfo = carinfo.replace("%", "проц.")
                urllib.request.urlretrieve(linkphoto, fr'data\data_photo/{user[0]}.jpg')
                sqlite3_query(f"UPDATE user SET message = '{carinfo}', count_ads = '{int(user[3])+1}' WHERE id = {user[0]}")

                with open(fr"data\log_data/{user[0]}.ini", "a+", encoding='utf-8-sig') as file:
                    file.write(carlink+"\n")
        else:
            print(f"[{emoji.emojize(blue_mark)}]LOG|[{datetime.now().time().replace(microsecond=0)}]|ID:{user[0]}|{user[1]}| No ads")
    except Exception as e:
        print(f"[{emoji.emojize(red_mark)}]LOG|[{datetime.now().time().replace(microsecond=0)}]| Error in parsing_information {e}")
        sleep(10)

def sqlite3_query(query):
    connect_to_DataBase = sqlite3.connect(r"data\users.db")
    cursor = connect_to_DataBase.cursor()
    cursor.execute(query)
    connect_to_DataBase.commit()
    result = cursor.fetchall()
    connect_to_DataBase.close()
    return result

if __name__ == '__main__':
    parsing()
