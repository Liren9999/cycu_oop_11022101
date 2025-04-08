# -*- coding: utf-8 -*-
import csv
import re
from playwright.sync_api import sync_playwright
import json


class BusRouteInfo:
    def __init__(self, routeid: str, direction: str = 'go'):
        self.rid = routeid
        self.content = None
        self.url = f'https://ebus.gov.taipei/Route/StopsOfRoute?routeid={routeid}'

        if direction not in ['go', 'come']:
            raise ValueError("Direction must be 'go' or 'come'")

        self.direction = direction
        self._fetch_content()

    def _fetch_content(self):
        # 使用 Playwright 瀏覽器來抓取網頁
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.url)
            
            if self.direction == 'come':
                page.click('a.stationlist-come-go-gray.stationlist-come')  # 點擊回程的按鈕
            
            page.wait_for_timeout(3000)  # 等待網頁加載完成
            self.content = page.content()
            browser.close()

        # 儲存網頁內容到本地檔案
        with open(f"data/ebus_taipei_{self.rid}.html", "w", encoding="utf-8") as file:
            file.write(self.content)

    def parse_and_save_to_csv(self):
        # 嘗試提取包含公車站資料的 JSON 資料，假設在某些 script 標籤中
        json_pattern = re.search(r'var busStopInfo = ({.*?});', self.content, re.DOTALL)
        
        if json_pattern:
            # 將 JSON 字串轉換為 Python 字典
            bus_stop_info = json.loads(json_pattern.group(1))
            
            bus_stop_data = []
            for stop in bus_stop_info:
                # 解析出每個站點的資料
                arrival_info = stop.get("arrival_info", "")
                stop_number = stop.get("stop_number", "")
                stop_name = stop.get("stop_name", "")
                stop_id = stop.get("stop_id", "")
                latitude = stop.get("latitude", "")
                longitude = stop.get("longitude", "")
                
                bus_stop_data.append([arrival_info, stop_number, stop_name, stop_id, latitude, longitude])
            
            # 儲存為 CSV 檔案
            csv_filename = f"data/bus_route_{self.rid}.csv"
            with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["arrival_info", "stop_number", "stop_name", "stop_id", "latitude", "longitude"])
                for row in bus_stop_data:
                    writer.writerow(row)
            
            print(f"Data has been written to {csv_filename}")
        else:
            print("No bus stop information found in the page content.")


# 範例使用
bus_route = BusRouteInfo('0100000A00')  # 輸入公車代碼
bus_route.parse_and_save_to_csv()  # 解析並儲存為 CSV
