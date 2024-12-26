import csv
import os
from random import random

from lxml import etree
import requests
from bs4 import BeautifulSoup

# The Latest instance present in the Database for Product Instance table
i=36

def webScrapeData(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }
    global i
    i=i+1
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract price
    price = soup.find("span", {"class": "a-price-whole"})
    price_element = price.get_text(strip=True) if price else "N/A"

    # Extract title
    title = soup.find("span", {"id": "productTitle"})
    title_text = title.get_text(strip=True) if title else "N/A"

    quantity =  int(random() * 100)
    print(f"Title: {title_text}, Price: {price_element}")
    soup = BeautifulSoup(response.text, "lxml")


    dom = etree.HTML(str(soup))


    xpath = '//*[@id="dpx-premium-sourced-badge-container"]/div/div[1]/span'
    element = dom.xpath(xpath)

    if element :
        element = element[0].text
    else:
        element = "N/A"


    return {"product_id": i,"quantity" : quantity,"product_name": title_text,"brand":element, "Price": price_element, "category" : 5}  # Return as dictionary


def save_to_csv(data, filename):
    if not data:
        print("No data to save.")
        return

    keys = data[0].keys()  # Get column names from the first dictionary
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()  # Write column headers
        writer.writerows(data)  # Write data rows

    print(f"Data saved to {filename}")


if __name__ == '__main__':
    urls = [
        "https://www.amazon.com/Roche-Posay-Lipikar-Intense-Repair-Cream/dp/B003QXZWYW/ref=lp_14717665011_1_2?pf_rd_p=53d84f87-8073-4df1-9740-1bf3fa798149&pf_rd_r=ACJZ0YZSPDNX8DQ2EKEX&sbo=RZvfv%2F%2FHxDF%2BO5021pAnSA%3D%3D",
        "https://www.amazon.com/Roche-Posay-Lipikar-Lotion-Repair-Moisturizing/dp/B075S2PFFM/ref=lp_14717665011_1_5?pf_rd_p=53d84f87-8073-4df1-9740-1bf3fa798149&pf_rd_r=ACJZ0YZSPDNX8DQ2EKEX&sbo=RZvfv%2F%2FHxDF%2BO5021pAnSA%3D%3D",
        "https://www.amazon.com/Eau-Thermale-Lipid-Replenishing-Eczema-Prone-Fragrance-Free/dp/B00EYOHGPU/ref=lp_14717665011_1_7?pf_rd_p=53d84f87-8073-4df1-9740-1bf3fa798149&pf_rd_r=ACJZ0YZSPDNX8DQ2EKEX&sbo=RZvfv%2F%2FHxDF%2BO5021pAnSA%3D%3D",
        "https://www.amazon.com/Eau-Thermale-Av%C3%A8ne-Ultra-Rich-Cleansing/dp/B07HWNL9W1/ref=lp_14717665011_1_12?pf_rd_p=53d84f87-8073-4df1-9740-1bf3fa798149&pf_rd_r=ACJZ0YZSPDNX8DQ2EKEX&sbo=RZvfv%2F%2FHxDF%2BO5021pAnSA%3D%3D",
        "https://www.amazon.com/CONTROL-CORRECTIVE-SKIN-CARE-SYSTEMS/dp/B01N9NUSOY/ref=sr_1_39?dib=eyJ2IjoiMSJ9.6U5rMqR-VmbKHYDp_xwF3haxYo2t4heyRIsEcNSE0bky_Oj_s6hKP4xNTNHR7gwB0xgr6Pc05ck4m0Cm70oyGJaHLBpEbRirdQak8ml2sBLLuah192GzP5N-2h3rQwqg-2rh2ijI6ebHDVDvGplyr9EU9APa0_J-w8dC2fLJtOKfdyo7sEjDQ9UrUs6x5siqx9nmVxISL2lpUWV_l-dj4T_J5vjnTebKEXMSColX6Z2It0BKK4GWn-ONabw9peC9VUXvRIaniTgDv8_1b0B0TiWqUuubsS_dvfDg5SFG-0k.rikU-gEdoGcJLqQvzbVGHKM0UPGLaUXldcjmsNMtGhw&dib_tag=se&qid=1733075058&s=beauty&sr=1-39&srs=14717665011",
        "https://www.amazon.com/dp/B0BRYNPN93/ref=sspa_dk_rhf_search_pt_sub_4/?_encoding=UTF8&ie=UTF8&psc=1&sp_csd=d2lkZ2V0TmFtZT1zcF9yaGZfc2VhcmNoX3BlcnNvbmFsaXplZA%3D%3D&pd_rd_w=P5IZM&content-id=amzn1.sym.ed82556b-5073-4521-a186-65fb40557bf5&pf_rd_p=ed82556b-5073-4521-a186-65fb40557bf5&pf_rd_r=1RJQXXY3FA5BQ05E1P98&pd_rd_wg=hAfQ7&pd_rd_r=3b675dcf-cf09-4fa3-b438-02f1d976b746&ref_=sspa_dk_rhf_search_pt_sub",
        "https://www.amazon.com/Replenix-Glycolic-Acid-Resurfacing-Lotion/dp/B0BG355ZL4/ref=sr_1_22?dib=eyJ2IjoiMSJ9.6U5rMqR-VmbKHYDp_xwF3haxYo2t4heyRIsEcNSE0bky_Oj_s6hKP4xNTNHR7gwB0xgr6Pc05ck4m0Cm70oyGJaHLBpEbRirdQak8ml2sBLLuah192GzP5N-2h3rQwqg-2rh2ijI6ebHDVDvGplyr9EU9APa0_J-w8dC2fLJtOKfdyo7sEjDQ9UrUs6x5siqx9nmVxISL2lpUWV_l-dj4T_J5vjnTebKEXMSColX6Z2It0BKK4GWn-ONabw9peC9VUXvRIaniTgDv8_1b0B0TiWqUuubsS_dvfDg5SFG-0k.rikU-gEdoGcJLqQvzbVGHKM0UPGLaUXldcjmsNMtGhw&dib_tag=se&qid=1733075058&rdc=1&s=beauty&sr=1-22&srs=14717665011",
        "https://www.amazon.com/Eau-Thermale-Av%C3%A8ne-XeraCalm-NUTRITION/dp/B0C5P331NJ/ref=sr_1_24?dib=eyJ2IjoiMSJ9.6U5rMqR-VmbKHYDp_xwF3haxYo2t4heyRIsEcNSE0bky_Oj_s6hKP4xNTNHR7gwB0xgr6Pc05ck4m0Cm70oyGJaHLBpEbRirdQak8ml2sBLLuah192GzP5N-2h3rQwqg-2rh2ijI6ebHDVDvGplyr9EU9APa0_J-w8dC2fLJtOKfdyo7sEjDQ9UrUs6x5siqx9nmVxISL2lpUWV_l-dj4T_J5vjnTebKEXMSColX6Z2It0BKK4GWn-ONabw9peC9VUXvRIaniTgDv8_1b0B0TiWqUuubsS_dvfDg5SFG-0k.rikU-gEdoGcJLqQvzbVGHKM0UPGLaUXldcjmsNMtGhw&dib_tag=se&qid=1733075058&s=beauty&sr=1-24&srs=14717665011"
    ]

    absolute_path = os.path.dirname(os.path.abspath(__file__))

    print("Absolute Path:", absolute_path)

    filename = absolute_path+ "/Amazon.csv"
    productData = []

    for url in urls:
        print(f"Scraping URL: {url}")
        data = webScrapeData(url)
        if data:
            productData.append(data)

    save_to_csv(productData, filename)