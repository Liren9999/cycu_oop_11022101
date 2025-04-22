import geopandas as gpd
import matplotlib.pyplot as plt
import os

def draw_geojson_to_png(inputfile: str, outputfile: str):
    # 顯示當前資料夾位置（方便除錯）
    print("目前工作資料夾：", os.getcwd())

    # 檢查檔案是否存在
    if not os.path.exists(inputfile):
        print(f"🚫 找不到檔案：{inputfile}")
        return

    # 讀取 GeoJSON 資料
    bus_stops = gpd.read_file(inputfile)

    # 關閉互動模式
    plt.ioff()

    # 繪圖
    fig, ax = plt.subplots(figsize=(10, 10))
    bus_stops.plot(ax=ax, color='blue', markersize=5)

    plt.title("Bus Stops", fontsize=16)
    plt.axis('equal')  # 維持經緯度比例

    # 儲存 PNG
    plt.savefig(outputfile, dpi=300)
    plt.close()
    print(f"✅ 圖已儲存為：{outputfile}")


if __name__ == "__main__":
    # 請改成你的實際檔案路徑
    inputfile = r"C:\Users\User\Desktop\cycu_oop_11022101\20250422\bus_stops.geojson"
    outputfile = "bus_stops.png"

    draw_geojson_to_png(inputfile, outputfile)