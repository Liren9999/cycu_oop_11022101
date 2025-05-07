# -*- coding: utf-8 -*-
import os
import csv
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# 確保 BusRouteInfo 類別定義在此檔案中
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
        # 模擬網頁請求的邏輯
        pass

    def _parse_and_save_to_csv(self):
        # 解析 HTML 並儲存為 CSV 的邏輯
        pass


def plot_bus_route_with_arrival_times(routeid: str, direction: str):
    # 確保 CSV 檔案已生成
    csv_filename = f"data/bus_route_{routeid}_{direction}.csv"
    if not os.path.exists(csv_filename):
        print(f"找不到路線資料檔案: {csv_filename}")
        return

    # 讀取 CSV 檔案
    df = pd.read_csv(csv_filename)
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)

    # 繪製地圖
    plt.figure(figsize=(10, 8))
    plt.plot(df['longitude'], df['latitude'], marker='o', color='blue', label='公車路線')

    # 加載圖示
    icon_path = r"C:\Users\User\Desktop\cycu_oop_11022101\data\bus_icon.png"
    bus_icon = None
    if os.path.exists(icon_path):
        bus_icon = plt.imread(icon_path)
    else:
        print(f"❌ 找不到圖示：{icon_path}")

    # 在地圖上標記每個車站
    for _, row in df.iterrows():
        arrival_info = row['arrival_info']
        lat, lon = row['latitude'], row['longitude']

        if arrival_info.isdigit():  # 如果到達時間是數字
            plt.text(lon, lat, f"{arrival_info} 分鐘", fontsize=10, color='red', ha='center', va='center')
        elif arrival_info == "進站中" and bus_icon is not None:  # 如果是「進站中」
            imagebox = OffsetImage(bus_icon, zoom=0.05)
            ab = AnnotationBbox(imagebox, (lon, lat), frameon=False)
            plt.gca().add_artist(ab)

    # 設定地圖標題和圖例
    plt.title(f"公車路線圖 - {routeid} ({direction})")
    plt.xlabel("經度")
    plt.ylabel("緯度")
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    # 讓使用者輸入公車代碼和方向
    routeid = input("請輸入公車代碼 (例如: 0100000A00): ").strip()
    direction = input("請輸入方向 ('go' 或 'come'): ").strip()

    # 生成公車路線資料
    route = BusRouteInfo(routeid=routeid, direction=direction)
    print(route.output)

    # 繪製公車路線圖
    plot_bus_route_with_arrival_times(routeid, direction)