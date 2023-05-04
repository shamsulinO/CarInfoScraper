import asyncio
import urllib.request
import re
from time import sleep

import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
browser = webdriver.Chrome(chrome_options=options, executable_path='chromedriver.exe')

async def bidfax_parsing(user_id, vin):
    try:
        ad_counter = 1
        browser.get("https://en.bidfax.info/")

        browser.execute_script(f"document.getElementById('search').setAttribute('value','{vin}');")
        browser.find_element(By.XPATH, "//input[@class='submit']").click()
        await asyncio.sleep(5)
        links_of_car = [link.get_attribute("href") for link in browser.find_elements(By.XPATH, "//div[@class='img-wrapper']//a")]

        adword = "объявление" if len(links_of_car) == 1 else "объявления" if len(links_of_car) >= 2 and len(links_of_car) <= 4 else "объявлений"
        if len(links_of_car) > 0: yield f"Я нашел *{len(links_of_car)}* {adword}, еще немного и я вам скину их! *:D*", False
        for car_ad in links_of_car:
            browser.get(car_ad)
            image_counter = 0

            image_urls = browser.execute_script("""
                var performance = window.performance || window.webkitPerformance || window.msPerformance || window.mozPerformance;
                var networkEntries = performance.getEntriesByType('resource');
                var imageUrls = [];
                for (var i = 0; i < networkEntries.length; i++) {
                    var entry = networkEntries[i];
                    if (entry.initiatorType == 'img') {
                        imageUrls.push(entry.name);
                    }
                }
                return imageUrls;
            """)

            for image in image_urls:
                if "-img" in image and image_counter < 10:
                    image_counter += 1

                    picture_request = urllib.request.urlopen(image, timeout=3)
                    with open(fr'data\data_photo/bidfax{user_id}img{image_counter}.jpg', "wb") as picture_file:
                        picture_file.write(picture_request.read())
                    await asyncio.sleep(0.1)

            car_name = browser.find_element(By.XPATH, "//div[@class='page-header full-title']").text
            car_name = re.search(r"(.+?) vin:", car_name).group(1)
            car_bid = "$" + browser.find_element(By.XPATH, "//span[@class='prices']").text

            car_lot = browser.find_element(By.XPATH, "//p[@class='short-story2']//span[@class='blackfont']").text
            car_date = browser.find_elements(By.XPATH, "//p[@class='short-story']//span[@class='blackfont']")[0].text
            car_condition = browser.find_elements(By.XPATH, "//p[@class='short-story2']//span[@class='blackfont']")[2].text
            car_primary_damage = browser.find_elements(By.XPATH, "//p[@class='short-story']//span[@class='blackfont']")[4].text
            car_secondary_damage = browser.find_elements(By.XPATH, "//p[@class='short-story2']//span[@class='blackfont']")[5].text

            yield f"[{car_name}]({car_ad})\n*Final bid*: `{car_bid}`\n*Lot*: `{car_lot}`\n*Date*: `{car_date}`\n*Car condition*: `{car_condition}`\n" \
                f"*Primary damage*: `{car_primary_damage}`\n*Secondary damage*: `{car_secondary_damage}`\n*{ad_counter}/{len(links_of_car)}*", image_counter
            ad_counter += 1

        if len(links_of_car) == 0:
            yield f"*Авто на BidFax не было найдено!*", False
    except Exception as e:
        yield f"*Ошибка*\nПовторите попытку.", False