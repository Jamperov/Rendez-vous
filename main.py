import json
import os.path

import requests
from bs4 import BeautifulSoup
import urllib3
import time
import random
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def get_data(url):
    headers = {
        "Accept" : "*/*",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36"
    }


    item_data_list = []

    iteration_count = 97
    print(f"Всего итераций: #{iteration_count}")
    for i in range(1,98):



        req = requests.get(url + f"{i}/?digiSearch=true&term=спортивная%20обувь&params=%7Csort%3DDEFAULT", headers=headers, verify=False)

        folder_name = f"data/data_{i}"

        if os.path.exists(folder_name):
            print("Папка уже существует")
        else:
            os.mkdir(folder_name)

        with open(f"{folder_name}/index_{i}.html", "w", encoding="utf-8") as file:
            file.write(req.text)
        with open(f"{folder_name}/index_{i}.html", "r", encoding="utf-8") as file:
            src = file.read()


        soup = BeautifulSoup(src, "lxml")
        items = soup.find_all("li", class_="item")
        item_urls = []


        for item in items:
            try:
                item_url = "https://www.rendez-vous.ru" + item.find("a", class_="item-link").get("href")
            except:
                continue
            item_urls.append(item_url)

        for item_url in item_urls:
            descriptions = []
            req = requests.get(item_url, headers=headers, verify=False)
            item_name = item_url.split("/")[-2]

            with open(f"{folder_name}/{item_name}.html", "w", encoding="utf-8") as file:
                file.write(req.text)
            with open(f"{folder_name}/{item_name}.html", "r", encoding="utf-8") as file:
                src = file.read()

            soup = BeautifulSoup(src, "lxml")
            item_data = soup.find("section", class_="item-details js-item")

            try:
                title = item_data.find("span", class_="item-name-title").text
            except:
                title = "The title was not found"

            try:
                store = item_data.find("span", class_="item-name-title").find("a").get_text()
            except:
                store = "The store was not found"
            link = item_url

            try:
                price = item_data.find("span", class_="item-price-value").text.strip()
                if " " in price:
                    price = price.replace(" ", "")
            except:
                price = "The price was not found"

            priceOld = None

            type = "normal"

            try:
                gender = item_data.find("span", class_="item-name-title").text.split(" ")[0]

                if gender != "Женские" and gender != "Мужские" and gender != "Детские":
                    gender = "Унисекс"
            except:
                gender = "The gender was not found"

            try:
                description = soup.find(class_="description").text.replace("\n", "").strip()

            except:
                description = "The description was not found"

            try:
                category = soup.find_all("a", itemprop="item")[2].get_text().split(" ")[1]
            except:
                category = "The category was not found"


            try:
                size = soup.find("ul", class_="form-select-list scrollbar scrollbar-y").find_all("li", class_="size")
                table_size = []
                for sizes in size:
                    item_size = sizes.text.replace("\n", "")
                    if "Подписаться" in item_size:
                        continue
                    table_size.append(
                        {
                            "title": "Size",
                            "value": item_size
                        }
                    )
            except:
                    table_size = "The size was not found"
            try:
                diff_description = []
                all_table = soup.find("div", class_="flex-grid-row").find_all("div", class_="flex-col-1")

                for diff in all_table:
                    dt = diff.find_all("dt")
                    dd = diff.find_all("dd")
                    for j in range(len(dt)):
                        col = dt[j].text
                        value = dd[j].text

                        diff_description.append(
                            {
                                "title": col,
                                "value": value
                            }
                        )
            except:
                diff_description = "The diff_info was notr found"
            try:
                description_long = soup.find("div", class_="description-long")
                description_long = description_long.get_text().replace("\n", "").strip()
            except:
                description_long = "The description long was not found"
            try:
                class_image = soup.find(class_="js-zoom-image")
                image_link = class_image.img["data-hight-src"]
            except:
                image_link = "The image was not found"
            try:
                for diff in diff_description:
                    if diff["title"] == "Страна происхождения бренда":
                        locale = diff["value"]
            except:
                locale = "The locale was not found"

            descriptions.append(
                {
                    "title" : "description",
                    "text" : description
                }
            )
            descriptions.append(
                {
                    "title": "size",
                    "text": "",
                    "table": table_size
                }
            )
            descriptions.append(
                {
                    "title": "other_info",
                    "value": diff_description
                }
            )
            descriptions.append(
                {
                    "title": "description_long",
                    "value": description_long
                }
            )
            descriptions.append(
                {
                    "title": "IMG",
                    "value": image_link
                }
            )

            item_data_list.append(
                {
                    "title" : title,
                    "store" : store,
                    "link" : link,
                    "price" : price,
                    "priceOld" : priceOld,
                    "type" : type,
                    "gender" : gender,
                    "description" : descriptions,
                    "category" : category,
                    "locale" : locale
                }
            )
        iteration_count -= 1
        print(f"Итерация #{i} завершена, осталось итераций #{iteration_count}")
        if iteration_count == 0:
            print("Сбор данных завершен!")
        time.sleep(random.randrange(2,4))
    with open("item_data.json", "a", encoding="utf-8") as file:
        json.dump(item_data_list, file, indent=4,  ensure_ascii=False)


get_data("https://www.rendez-vous.ru/catalog/female/krossovki/page/")
