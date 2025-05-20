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
        
        # 定义北北基桃的县市名称列表
        # 请根据您的shapefile中实际的县市名称进行调整
        # 常见的写法包括 '臺北市', '新北市', '基隆市', '桃園市' 或 '台北市', '新北市', '基隆市', '桃园市'
        # 建议您检查 shapefile 的属性表，确认 COUNTYNAME 字段的实际值
        
        # 这里使用一种兼容性更强的方式：检查是否包含关键字
        north_regions_names = ['臺北市', '新北市', '基隆市', '桃園市', '台北市', '新北市', '基隆市', '桃园市'] 
        
        # 假设县市名称的字段是 'COUNTYNAME'。如果不是，请修改这里的字段名。
        # 检查 combined_gdf 中是否存在 'COUNTYNAME' 列
        if 'COUNTYNAME' in combined_gdf.columns:
            # 筛选 GeoDataFrame
            # 使用 .isin() 方法进行筛选，匹配 exact names
            # 或者使用 .str.contains() 如果名称不完全匹配，例如 '新北' 包含在 '新北市'
            
            # 使用 isin() 进行精确匹配（推荐，如果数据一致）
            north_regions_gdf = combined_gdf[
                combined_gdf['COUNTYNAME'].isin(['臺北市', '新北市', '基隆市', '桃園市']) |
                combined_gdf['COUNTYNAME'].isin(['台北市', '新北市', '基隆市', '桃园市'])
            ].copy() # .copy() 避免SettingWithCopyWarning

            if north_regions_gdf.empty:
                print("No North-North-Keelung-Taoyuan regions found with 'COUNTYNAME' column using specified names.")
                print("Available COUNTYNAMEs:", combined_gdf['COUNTYNAME'].unique())
            else:
                # 绘制北北基桃的 GeoDataFrame
                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                
                # 可以根据 COUNTYNAME 为不同的市涂上不同的颜色
                north_regions_gdf.plot(ax=ax, edgecolor='black', linewidth=0.5, 
                                       column='COUNTYNAME', cmap='Paired', legend=True)
                
                plt.title("Map of Taipei, New Taipei, Keelung, Taoyuan (北北基桃)")
                plt.axis('equal')
                plt.show()

                print("Successfully plotted North-North-Keelung-Taoyuan regions.")
        else:
            print("The GeoDataFrame does not have a 'COUNTYNAME' column. Cannot filter by county name.")
            print("Available columns:", combined_gdf.columns.tolist())
            # 如果没有 COUNTYNAME，可能需要查看其他列来确定行政区划信息
            # 或者先绘制全部，手动判断哪个列是县市名称
            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            combined_gdf.plot(ax=ax, edgecolor='black', linewidth=0.5, cmap='viridis')
            plt.title("Combined Shapefiles (No COUNTYNAME column found)")
            plt.axis('equal')
            plt.show()