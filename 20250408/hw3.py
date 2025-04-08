from playwright.sync_api import sync_playwright
import csv
import json
import time

def fetch_bus_route_with_playwright(route_id):
    url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 請求目標網址
        page.goto(url)
        
        # 等待特定的元素出現
        try:
            page.wait_for_selector("script[type='text/javascript']", timeout=60000)  # 等待 60 秒
        except Exception as e:
            print(f"Error waiting for selector: {e}")
            browser.close()
            return
        
        # 嘗試抓取包含 JSON 資料的 <script> 標籤
        try:
            script_tag = page.query_selector("script[type='text/javascript']")
            if not script_tag:
                print("Unable to find script tag containing data.")
                print("Page content:", page.content())  # 打印頁面內容以除錯
                browser.close()
                return
            
            # 解析 JavaScript 變數中的 JSON 資料
            script_content = script_tag.inner_text()
            json_data = script_content.split('=')[-1].strip().strip(';')
            data = json.loads(json_data)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            browser.close()
            return
        
        # 擷取公車站資料
        bus_stops = data.get("stops", [])
        if not bus_stops:
            print("No bus stops found in the data.")
            browser.close()
            return
        
        # 準備 CSV 檔案標題欄位
        csv_filename = f"{route_id}_bus_route.csv"
        csv_headers = ["arrival_info", "stop_number", "stop_name", "stop_id", "latitude", "longitude"]
        
        # 將資料寫入 CSV
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(csv_headers)
            
            for stop in bus_stops:
                row = [
                    stop.get("arrival_info", ""),
                    stop.get("stop_number", ""),
                    stop.get("stop_name", ""),
                    stop.get("stop_id", ""),
                    stop.get("latitude", ""),
                    stop.get("longitude", "")
                ]
                writer.writerow(row)
        
        print(f"Data has been written to {csv_filename}")
        browser.close()

# 範例使用
fetch_bus_route_with_playwright("0100000A00")