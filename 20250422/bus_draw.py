import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import json

def draw_bus_routes_from_geojson(geojson_file, route1_stations, route2_stations, outputfile):
    """
    繪製承德幹線和基隆幹線的車站路線圖。

    :param geojson_file: GeoJSON 檔案路徑
    :param route1_stations: 承德幹線的車站名稱列表
    :param route2_stations: 基隆幹線的車站名稱列表
    :param outputfile: 輸出的 PNG 檔案路徑
    """
    # 讀取 GeoJSON 檔案
    with open(geojson_file, 'r', encoding='utf-8') as file:
        geojson_data = json.load(file)

    # 提取車站資料
    features = geojson_data['features']
    stations = []
    for feature in features:
        name = feature['properties']['BSM_CHINES']
        coordinates = feature['geometry']['coordinates']
        stations.append({'name': name, 'longitude': coordinates[0], 'latitude': coordinates[1]})

    # 轉換為 DataFrame
    stations_df = pd.DataFrame(stations)

    # 過濾承德幹線和基隆幹線的車站
    route1_df = stations_df[stations_df['name'].isin(route1_stations)]
    route2_df = stations_df[stations_df['name'].isin(route2_stations)]

    # 繪圖
    plt.figure(figsize=(10, 10))

    # 繪製承德幹線
    if not route1_df.empty:
        plt.plot(route1_df['longitude'], route1_df['latitude'], color='blue', marker='o', label='承德幹線')
        for lon, lat, name in zip(route1_df['longitude'], route1_df['latitude'], route1_df['name']):
            plt.text(lon, lat, name, fontsize=8, color='blue')

    # 繪製基隆幹線
    if not route2_df.empty:
        plt.plot(route2_df['longitude'], route2_df['latitude'], color='red', marker='o', label='基隆幹線')
        for lon, lat, name in zip(route2_df['longitude'], route2_df['latitude'], route2_df['name']):
            plt.text(lon, lat, name, fontsize=8, color='red')

    # 設定圖例和標題
    plt.title("Bus Routes: 承德幹線 & 基隆幹線", fontsize=16)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()

    # 儲存圖片
    plt.savefig(outputfile, dpi=300)
    plt.close()
    print(f"✅ 圖已儲存為：{outputfile}")


if __name__ == "__main__":
    # GeoJSON 檔案路徑
    geojson_file = r"C:\Users\User\Desktop\cycu_oop_11022101\20250422\bus_stops.geojson"

    # 承德幹線和基隆幹線的車站名稱
    chengde_stations = ["捷運西湖站", "福美站", "法藏寺"]
    keelung_stations = ["新店國小", "文山國中", "碧潭"]

    # 輸出的圖片檔案
    outputfile = "bus_routes.png"

    # 繪製路線圖
    draw_bus_routes_from_geojson(geojson_file, chengde_stations, keelung_stations, outputfile)