import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd

# 找出 taipei_town 目錄下的所有 .shp 檔案
shp_dir = "20250520/taipei_town"
shp_files = []
for fname in os.listdir(shp_dir):
    if fname.endswith(".shp"):
        shp_files.append(os.path.join(shp_dir, fname))

if not shp_files:
    print(f"No shapefiles found in {shp_dir}")
else:
    gdfs = []
    for shp_file in shp_files:
        try:
            gdf_temp = gpd.read_file(shp_file)
            gdfs.append(gdf_temp)
            print(f"Successfully loaded: {shp_file}")
        except Exception as e:
            print(f"Error loading {shp_file}: {e}")

    if not gdfs:
        print("No GeoDataFrames could be loaded.")
    else:
        # 统一所有GeoDataFrame的CRS
        crs_to_use = gdfs[0].crs
        aligned_gdfs = []
        for gdf in gdfs:
            if gdf.crs != crs_to_use:
                aligned_gdfs.append(gdf.to_crs(crs_to_use))
            else:
                aligned_gdfs.append(gdf)

        combined_gdf = pd.concat(aligned_gdfs, ignore_index=True)

        # --- 筛选出北北基桃区域 ---
        north_regions_names = ['臺北市', '新北市', '基隆市', '桃園市', '台北市', '新北市', '基隆市', '桃园市']

        if 'COUNTYNAME' in combined_gdf.columns:
            north_regions_gdf = combined_gdf[
                combined_gdf['COUNTYNAME'].isin(north_regions_names)
            ].copy()

            if north_regions_gdf.empty:
                print("No North-North-Keelung-Taoyuan regions found with 'COUNTYNAME' column using specified names.")
                print("Available COUNTYNAMEs:", combined_gdf['COUNTYNAME'].unique())
            else:
                # 绘制北北基桃的 GeoDataFrame
                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                north_regions_gdf.plot(ax=ax, edgecolor='black', linewidth=0.5, 
                                       column='COUNTYNAME', cmap='Paired', legend=True)

                plt.title("Map of Taipei, New Taipei, Keelung, Taoyuan (北北基桃)")
                plt.axis('equal')

                # 保存為 JPG 檔案
                output_dir = r"C:\Users\User\Desktop\cycu_oop_11022101\data"
                os.makedirs(output_dir, exist_ok=True)  # 確保目錄存在
                output_path = os.path.join(output_dir, "north_regions_map.jpg")
                plt.savefig(output_path, format='jpg', dpi=300)
                print(f"Map saved as JPG at: {output_path}")

                plt.show()

        else:
            print("The GeoDataFrame does not have a 'COUNTYNAME' column. Cannot filter by county name.")
            print("Available columns:", combined_gdf.columns.tolist())
            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            combined_gdf.plot(ax=ax, edgecolor='black', linewidth=0.5, cmap='viridis')
            plt.title("Combined Shapefiles (No COUNTYNAME column found)")
            plt.axis('equal')
            plt.show()