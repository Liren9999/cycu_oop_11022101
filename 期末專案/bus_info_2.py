# -*- coding: utf-8 -*-
import os
import csv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time


class BusRouteInfo:
    def __init__(self, routeid: str, direction: str = 'go'):
        self.rid = routeid
        self.content = None
        self.url = f'https://ebus.gov.taipei/Route/StopsOfRoute?routeid={routeid}'

        if direction not in ['go', 'come']:
            raise ValueError("Direction must be 'go' or 'come'")

        self.direction = direction

        self._fetch_content()
        self.output = self._parse_and_save_to_csv()

    def _fetch_content(self):
        retries = 3  # 最大重試次數
        while retries > 0:
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(self.url)

                    if self.direction == 'come':
                        # 切換到返程
                        page.click('a.stationlist-come-go-gray.stationlist-come')

                    # 等待站點資訊載入完成
                    page.wait_for_selector('.auto-list-stationlist', timeout=10000)
                    time.sleep(5)  # 等待 5 秒以確保載入完成
                    self.content = page.content()
                    browser.close()
                    break  # 成功抓取後跳出重試迴圈
            except Exception as e:
                print(f"等待目標元素時發生錯誤: {e}")
                retries -= 1
                time.sleep(5)  # 等待 5 秒後重試

        if not self.content:
            print(f"無法抓取公車代碼 {self.rid} 的資料，方向: {self.direction}")

        # 儲存 HTML 內容到檔案（除錯用）
        os.makedirs("data", exist_ok=True)  # 確保資料夾存在
        with open(f"data/ebus_taipei_{self.rid}_{self.direction}.html", "w", encoding="utf-8") as file:
            file.write(self.content or "")

    def _parse_and_save_to_csv(self):
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(self.content, 'html.parser') if self.content else None
        stops = []

        if not soup:
            return "無法解析 HTML 內容，請檢查網頁結構或連線問題。"

        # 根據提供的 HTML 結構，選擇站點資訊
        stop_elements = soup.select('.auto-list-stationlist')  # 修改選擇器以符合實際網站結構
        if not stop_elements:
            return "無法找到站點資訊，請檢查選擇器或網站結構。"

        for stop in stop_elements:
            try:
                # 提取站點資訊
                arrival_info = stop.select_one('.auto-list-stationlist-position').text.strip()
                if not arrival_info:  # 如果沒有到達時間，跳過該站點
                    continue

                if "進站中" in arrival_info:
                    arrival_info = "進站中"
                elif "尚未發車" in arrival_info:
                    arrival_info = "尚未發車"

                stop_number = stop.select_one('.auto-list-stationlist-number').text.strip()  # 車站序號
                stop_name = stop.select_one('.auto-list-stationlist-place').text.strip()  # 車站名稱
                stop_id = stop.select_one('input[name="item.UniStopId"]')['value']  # 車站編號
                latitude = stop.select_one('input[name="item.Latitude"]')['value']  # 緯度
                longitude = stop.select_one('input[name="item.Longitude"]')['value']  # 經度

                stops.append([arrival_info, stop_number, stop_name, stop_id, latitude, longitude])
            except AttributeError:
                # 不顯示錯誤訊息，直接跳過
                continue

        # 確保資料夾存在
        os.makedirs("data/BUS_INFO", exist_ok=True)

        # 將資料寫入 CSV
        csv_filename = f"data/BUS_INFO/bus_route_{self.rid}_{self.direction}.csv"
        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["arrival_info", "stop_number", "stop_name", "stop_id", "latitude", "longitude"])
            writer.writerows(stops)

        output = [f"資料已儲存至 {csv_filename}"]
        for stop in stops:
            output.append(f"公車到達時間: {stop[0]}, 車站序號: {stop[1]}, 車站名稱: {stop[2]}, 車站編號: {stop[3]}, 緯度: {stop[4]}, 經度: {stop[5]}")
        return "\n".join(output)


def fetch_all_routes():
    """
    從網站中抓取所有公車代碼，並依序讀取每個公車代碼的車站資料。
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://ebus.gov.taipei/ebus")

        try:
            # 等待公車代碼載入完成
            page.wait_for_selector('a[href^="javascript:go"]', timeout=10000)
            time.sleep(5)  # 等待 5 秒以確保載入完成

            # 抓取所有公車代碼
            soup = BeautifulSoup(page.content(), 'html.parser')
            route_links = soup.select('a[href^="javascript:go"]')
            route_ids = [link['href'].split("'")[1] for link in route_links]
        except Exception as e:
            print(f"抓取公車代碼時發生錯誤: {e}")
            route_ids = []
        finally:
            browser.close()

    # 依序讀取每個公車代碼的車站資料
    for routeid in route_ids:
        for direction in ['go', 'come']:
            csv_filename = f"data/BUS_INFO/bus_route_{routeid}_{direction}.csv"
            if os.path.exists(csv_filename):
                print(f"檔案 {csv_filename} 已存在，跳過抓取。")
                continue

            try:
                print(f"正在處理公車代碼: {routeid}, 方向: {direction}")
                bus_route = BusRouteInfo(routeid, direction)  # 使用 BusRouteInfo 類別
                print(bus_route.output)
            except Exception as e:
                print(f"處理公車代碼 {routeid} 時發生錯誤: {e}")


if __name__ == "__main__":
    fetch_all_routes()