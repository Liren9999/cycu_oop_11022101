# -*- coding: utf-8 -*-
import os
import csv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd
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
                page.wait_for_selector('.auto-list-stationlist', timeout=10000)
                self.content = page.content()
            except Exception as e:
                print(f"等待目標元素時發生錯誤: {e}")
                self.content = None
            finally:
                browser.close()

        os.makedirs("data", exist_ok=True)
        with open(f"data/ebus_taipei_{self.rid}.html", "w", encoding="utf-8") as file:
            file.write(self.content or "")

    def _parse_and_save_to_csv(self):
        soup = BeautifulSoup(self.content, 'html.parser') if self.content else None
        stops = []

        if not soup:
            return "無法解析 HTML 內容，請檢查網頁結構或連線問題。"

        stop_elements = soup.select('.auto-list-stationlist')
        if not stop_elements:
            return "無法找到站點資訊，請檢查選擇器或網站結構。"

        for stop in stop_elements:
            try:
                arrival_info = stop.select_one('.auto-list-stationlist-position-time').text.strip()
                stop_number = stop.select_one('.auto-list-stationlist-number').text.strip()
                stop_name = stop.select_one('.auto-list-stationlist-place').text.strip()
                stop_id = stop.select_one('input[name="item.UniStopId"]')['value']
                latitude = stop.select_one('input[name="item.Latitude"]')['value']
                longitude = stop.select_one('input[name="item.Longitude"]')['value']

                stops.append([arrival_info, stop_number, stop_name, stop_id, latitude, longitude])
            except AttributeError:
                continue

        os.makedirs("data", exist_ok=True)
        csv_filename = f"data/bus_route_{self.rid}.csv"
        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["arrival_info", "stop_number", "stop_name", "stop_id", "latitude", "longitude"])
            writer.writerows(stops)

        return stops


def plot_route_with_marker(routeid: str, target_stop: str):
    csv_filename = f"data/bus_route_{routeid}.csv"
    if not os.path.exists(csv_filename):
        print(f"找不到路線資料檔案: {csv_filename}")
        return

    df = pd.read_csv(csv_filename)
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)

    plt.figure(figsize=(10, 8))
    plt.plot(df['longitude'], df['latitude'], marker='o', color='blue', label='公車路線')

    target_row = df[df['stop_name'].str.strip() == target_stop.strip()]
    if not target_row.empty:
        target_lat = float(target_row.iloc[0]['latitude'])
        target_lon = float(target_row.iloc[0]['longitude'])

        icon_path = "data/person_icon.png"
        if os.path.exists(icon_path):
            img = plt.imread(icon_path)
            imagebox = OffsetImage(img, zoom=0.1)
            ab = AnnotationBbox(imagebox, (target_lon, target_lat), frameon=False)
            plt.gca().add_artist(ab)
        else:
            print("❌ 找不到小人圖示：請確認 'data/person_icon.png' 是否存在。")
    else:
        print(f"⚠️ 找不到指定車站：{target_stop}")

    plt.title(f"公車路線圖 - {routeid}")
    plt.xlabel("經度")
    plt.ylabel("緯度")
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    routeid = input("請輸入公車代碼 (例如: 0100000A00): ").strip()
    direction = input("請輸入方向 ('go' 或 'come'): ").strip()

    route = BusRouteInfo(routeid=routeid, direction=direction)
    stops = route.output

    print("以下是此路線的所有車站名稱：")
    for stop in stops:
        print(stop[2])  # 車站名稱

    target_stop = input("請輸入目標車站名稱：").strip()
    plot_route_with_marker(routeid, target_stop)
