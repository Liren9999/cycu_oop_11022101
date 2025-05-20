import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from PIL import Image

# 讀取承德幹線和基隆幹線的 CSV 檔案
chengde_path = r"C:\Users\User\Desktop\cycu_oop_11022101\data\bus_route_0161000900.csv"
keelung_path = r"C:\Users\User\Desktop\cycu_oop_11022101\data\bus_route_0161001500.csv"

chengde_df = pd.read_csv(chengde_path)
keelung_df = pd.read_csv(keelung_path)

# 讀取 GeoJSON 檔案
geojson_path = r"C:\Users\User\Desktop\cycu_oop_11022101\20250422\bus_stops.geojson"
geojson_data = gpd.read_file(geojson_path)

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

# 計算經緯度範圍，確保兩條路線的範圍一致
min_lon = min(chengde_coords['longitude'].min(), keelung_coords['longitude'].min())
max_lon = max(chengde_coords['longitude'].max(), keelung_coords['longitude'].max())
min_lat = min(chengde_coords['latitude'].min(), keelung_coords['latitude'].min())
max_lat = max(chengde_coords['latitude'].max(), keelung_coords['latitude'].max())

# 讀取背景圖片
background_image_path = r"C:\Users\User\Desktop\cycu_oop_11022101\data\north_regions_map.jpg"
img = Image.open(background_image_path)

# 繪製地圖
fig, ax = plt.subplots(figsize=(12, 10))

# 顯示背景圖片，範圍與公車站點對齊
ax.imshow(img, extent=[min_lon, max_lon, min_lat, max_lat], aspect='auto')

# 繪製承德幹線
ax.plot(chengde_coords['longitude'], chengde_coords['latitude'], marker='o', color='blue', label='承德幹線')

# 繪製基隆幹線
ax.plot(keelung_coords['longitude'], keelung_coords['latitude'], marker='o', color='green', label='基隆幹線')

# 添加標籤和圖例
ax.set_title("承德幹線與基隆幹線車站路線圖與北北基桃區界圖", fontsize=16)
ax.set_xlabel("經度", fontsize=12)
ax.set_ylabel("緯度", fontsize=12)
ax.legend()

# 顯示地圖
plt.tight_layout()
plt.show()