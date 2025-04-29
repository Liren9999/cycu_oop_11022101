# -*- coding: utf-8 -*-
import os
import csv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


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
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.url)
            
            if self.direction == 'come':
                page.click('a.stationlist-come-go-gray.stationlist-come')
            
            try:
                # 等待站點資訊載入完成
                page.wait_for_selector('.auto-list-stationlist', timeout=10000)  # 最多等待 10 秒
                self.content = page.content()
            except Exception as e:
                print(f"等待目標元素時發生錯誤: {e}")
                self.content = None
            finally:
                browser.close()

        # 儲存 HTML 內容到檔案（除錯用）
        os.makedirs("data", exist_ok=True)  # 確保資料夾存在
        with open(f"data/ebus_taipei_{self.rid}.html", "w", encoding="utf-8") as file:
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
                arrival_info = stop.select_one('.auto-list-stationlist-position-time').text.strip()  # 到達時間
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
        os.makedirs("data", exist_ok=True)

        # 將資料寫入 CSV
        csv_filename = f"data/bus_route_{self.rid}.csv"
        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["arrival_info", "stop_number", "stop_name", "stop_id", "latitude", "longitude"])
            writer.writerows(stops)

        output = [f"資料已儲存至 {csv_filename}"]
        for stop in stops:
            output.append(f"公車到達時間: {stop[0]}, 車站序號: {stop[1]}, 車站名稱: {stop[2]}, 車站編號: {stop[3]}, 緯度: {stop[4]}, 經度: {stop[5]}")
        return stops


def plot_route_with_marker(routeid: str, target_stop: str):
    # 讀取 CSV 檔案
    csv_filename = f"data/bus_route_{routeid}.csv"
    if not os.path.exists(csv_filename):
        print(f"找不到路線資料檔案: {csv_filename}")
        return

    df = pd.read_csv(csv_filename)

    # 繪製路線圖
    plt.figure(figsize=(10, 8))
    plt.plot(df['longitude'], df['latitude'], marker='o', color='blue', label='公車路線')

    # 找到目標車站
    target_row = df[df['stop_name'] == target_stop]
    if not target_row.empty:
        target_lat = target_row.iloc[0]['latitude']
        target_lon = target_row.iloc[0]['longitude']

        # 繪製小人圖示
        img = plt.imread("data/person_icon.png")  # 確保有小人圖示檔案
        imagebox = OffsetImage(img, zoom=0.1)
        ab = AnnotationBbox(imagebox, (target_lon, target_lat), frameon=False)
        plt.gca().add_artist(ab)

    # 添加標籤和圖例
    plt.title(f"公車路線圖 - {routeid}")
    plt.xlabel("經度")
    plt.ylabel("緯度")
    plt.legend()
    plt.grid()

    # 顯示圖表
    plt.show()


if __name__ == "__main__":
    # 讓使用者輸入公車代碼和方向
    routeid = input("請輸入公車代碼 (例如: 0100000A00): ").strip()
    direction = input("請輸入方向 ('go' 或 'come'): ").strip()

    # 取得公車路線資訊
    route = BusRouteInfo(routeid=routeid, direction=direction)
    stops = route.output

    # 列出所有車站名稱
    print("以下是此路線的所有車站名稱：")
    for stop in stops:
        print(stop[2])  # 車站名稱

    # 輸入目標車站
    target_stop = input("請輸入目標車站名稱：").strip()

    # 繪製路線圖並標記目標車站
    plot_route_with_marker(routeid, target_stop)