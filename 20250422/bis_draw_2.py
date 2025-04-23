import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# 讀取承德幹線和基隆幹線的 CSV 檔案
chengde_path = r"C:\Users\User\Desktop\cycu_oop_11022101\data\bus_route_0161000900.csv"
keelung_path = r"C:\Users\User\Desktop\cycu_oop_11022101\data\bus_route_0161001500.csv"

chengde_df = pd.read_csv(chengde_path)
keelung_df = pd.read_csv(keelung_path)

# 讀取 GeoJSON 檔案
geojson_path = r"C:\Users\User\Desktop\cycu_oop_11022101\20250422\bus_stops.geojson"
geojson_data = gpd.read_file(geojson_path)

# 檢查 GeoJSON 結構
print(geojson_data.head())

# 修正提取資料的方式
geojson_data['stop_name'] = geojson_data['BSM_CHINES']
geojson_data['latitude'] = geojson_data.geometry.y
geojson_data['longitude'] = geojson_data.geometry.x

# 定義一個函數來匹配車站名稱並提取經緯度
def match_coordinates(df, geojson_data):
    matched_data = []
    for _, row in df.iterrows():
        stop_name = row['stop_name']
        match = geojson_data[geojson_data['stop_name'] == stop_name]
        if not match.empty:
            matched_data.append({
                'stop_name': stop_name,
                'latitude': match.iloc[0]['latitude'],
                'longitude': match.iloc[0]['longitude']
            })
    return pd.DataFrame(matched_data)

# 匹配承德幹線和基隆幹線的經緯度
chengde_coords = match_coordinates(chengde_df, geojson_data)
keelung_coords = match_coordinates(keelung_df, geojson_data)

# 繪製路線圖
plt.figure(figsize=(10, 8))

# 繪製承德幹線
plt.plot(chengde_coords['longitude'], chengde_coords['latitude'], marker='o', color='blue', label='承德幹線')

# 繪製基隆幹線
plt.plot(keelung_coords['longitude'], keelung_coords['latitude'], marker='o', color='green', label='基隆幹線')

# 添加標籤和圖例
plt.title("承德幹線與基隆幹線車站路線圖")
plt.xlabel("經度")
plt.ylabel("緯度")
plt.legend()
plt.grid()

# 顯示圖表
plt.show()