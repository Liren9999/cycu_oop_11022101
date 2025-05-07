# -*- coding: utf-8 -*-
import os
import csv
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from hw2_2_finals_finsh import BusRouteInfo  # 引入 BusRouteInfo 類別

# 設置支持中文的字體
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 設置支持中文的字體
matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題

def plot_route_with_arrival_times_and_icons(routeid: str, direction: str, target_stop_number: str = None):
    # 確保 CSV 檔案已生成
    csv_filename = f"data/bus_route_{routeid}_{direction}.csv"
    if not os.path.exists(csv_filename):
        print(f"找不到路線資料檔案: {csv_filename}")
        return

    # 讀取 CSV 檔案
    df = pd.read_csv(csv_filename)
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    df['stop_number'] = df['stop_number'].astype(str)  # 將 stop_number 轉換為字串

    # 繪製地圖
    plt.figure(figsize=(10, 8))
    plt.plot(df['longitude'], df['latitude'], marker='o', color='blue', label='公車路線')

    # 加載圖示
    bus_icon_path = r"C:\Users\User\Desktop\cycu_oop_11022101\data\bus_icon.png"
    person_icon_path = r"C:\Users\User\Desktop\cycu_oop_11022101\data\person_icon.png"
    bus_icon = None
    person_icon = None

    if os.path.exists(bus_icon_path):
        bus_icon = plt.imread(bus_icon_path)
    else:
        print(f"❌ 找不到公車圖示：{bus_icon_path}")

    if os.path.exists(person_icon_path):
        person_icon = plt.imread(person_icon_path)
    else:
        print(f"❌ 找不到小人圖示：{person_icon_path}")

    # 在地圖上標記每個車站
    for _, row in df.iterrows():
        arrival_info = row['arrival_info']
        lat, lon = row['latitude'], row['longitude']
        stop_name = row['stop_name']
        stop_number = row['stop_number']

        # 處理到達時間
        if "分鐘" in arrival_info:
            arrival_info = arrival_info.replace("分鐘", "").strip()

        if arrival_info.isdigit():  # 如果到達時間是數字
            # 顯示到達時間（例如：4min）
            plt.text(lon + 0.0001, lat + 0.0001, f"{arrival_info}min", fontsize=10, color='red', ha='left', va='bottom')
        elif arrival_info == "進站中" and bus_icon is not None:  # 如果是「進站中」
            # 顯示公車圖示
            imagebox = OffsetImage(bus_icon, zoom=0.05)
            ab = AnnotationBbox(imagebox, (lon, lat), frameon=False)
            plt.gca().add_artist(ab)

        # 顯示車站名稱（英文）
        plt.text(lon, lat - 0.0005, stop_name, fontsize=8, color='blue', ha='center', va='top')

        # 如果是目標車站，顯示小人圖示
        if target_stop_number and stop_number.strip() == target_stop_number.strip() and person_icon is not None:
            imagebox = OffsetImage(person_icon, zoom=0.1)
            ab = AnnotationBbox(imagebox, (lon, lat), frameon=False)
            plt.gca().add_artist(ab)

    # 設定地圖標題和圖例
    plt.title(f"Bus Route Map - {routeid} ({direction})")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
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

    # 顯示所有車站名稱和 stop_number
    csv_filename = f"data/bus_route_{routeid}_{direction}.csv"
    if os.path.exists(csv_filename):
        df = pd.read_csv(csv_filename)
        print("以下是此路線的所有車站名稱及其 stop_number：")
        for _, row in df.iterrows():
            print(f"車站名稱: {row['stop_name']}, stop_number: {row['stop_number']}")

    # 讓使用者選擇目標車站
    target_stop_number = input("請輸入目標車站的 stop_number（可選，按 Enter 跳過）：").strip()

    # 繪製公車路線圖
    plot_route_with_arrival_times_and_icons(routeid, direction, target_stop_number)