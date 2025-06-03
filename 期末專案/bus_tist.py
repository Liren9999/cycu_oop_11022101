# -*- coding: utf-8 -*-
import os
import csv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def fetch_bus_routes():
    """
    從網站中抓取所有公車代碼和名稱，並儲存為 CSV 檔案。
    """
    url = "https://ebus.gov.taipei/ebus"
    data_folder = "C:/Users/User/Desktop/cycu_oop_11022101/data"
    csv_filename = os.path.join(data_folder, "bus_info_tist.csv")

    # 確保資料夾存在
    os.makedirs(data_folder, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        try:
            # 等待目標元素載入完成
            page.wait_for_selector('a[href^="javascript:go"]', timeout=10000)

            # 抓取網頁內容
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # 抓取所有公車代碼和名稱
            route_links = soup.select('a[href^="javascript:go"]')
            bus_routes = [[link['href'].split("'")[1], link.text.strip()] for link in route_links]

            # 將資料寫入 CSV
            with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Route ID", "Route Name"])  # CSV 標題列
                writer.writerows(bus_routes)

            print(f"資料已成功儲存至 {csv_filename}")
        except Exception as e:
            print(f"抓取公車代碼時發生錯誤: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    fetch_bus_routes()