import folium
import random
import time
import webbrowser
import re
import csv
import asyncio

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 站牌資料解析
def extract_stops_from_soup(soup, direction_type, route_id):
    stops_with_coords = []
    estimated_times = {}

    if direction_type == "去程":
        direction_container = soup.find('div', id='GoDirectionRoute')
    elif direction_type == "返程":
        direction_container = soup.find('div', id='BackDirectionRoute')
    else:
        print(f"錯誤：未知方向類型 '{direction_type}'。")
        return [], {}

    if not direction_container:
        print(f"未找到 {direction_type} 方向的內容容器。")
        return [], {}

    all_stop_list_items = direction_container.find_all('li')

    if not all_stop_list_items:
        print(f"在 {direction_type} 方向中未找到任何站牌列表項目。")
        return [], {}

    for item in all_stop_list_items:
        item_html = str(item)
        stop_name_tag = item.find('span', class_='auto-list-stationlist-place')
        stop_name = stop_name_tag.get_text().strip() if stop_name_tag else "未知站名"

        stop_id_match = re.search(r'<input[^>]+name="item\.UniStopId"[^>]+value="(\d+)"[^>]*>', item_html)
        lat_match = re.search(r'<input[^>]+name="item\.Latitude"[^>]+value="([\d\.]+)"[^>]*>', item_html)
        lon_match = re.search(r'<input[^>]+name="item\.Longitude"[^>]+value="([\d\.]+)"[^>]*>', item_html)

        stop_id = int(stop_id_match.group(1)) if stop_id_match and stop_id_match.group(1).isdigit() else None
        lat = float(lat_match.group(1)) if lat_match else None
        lon = float(lon_match.group(1)) if lon_match else None

        if lat is not None and lon is not None:
            stops_with_coords.append({
                "name": stop_name,
                "lat": lat,
                "lon": lon,
                "stop_id": stop_id,
                "direction": direction_type
            })
        else:
            print(f"警告：站點 '{stop_name}' 經緯度無效，已跳過。")

        eta_text = "查無資訊"
        eta_tag_onroad = item.find('span', class_='eta_onroad')
        if eta_tag_onroad and eta_tag_onroad.get_text().strip() != '':
            eta_text = eta_tag_onroad.get_text().strip()
        else:
            eta_tag_static = item.find('span', class_='auto-list-stationlist-position-time')
            if eta_tag_static and eta_tag_static.get_text().strip() != '':
                eta_text = eta_tag_static.get_text().strip()
        estimated_times[f"{stop_name}_{direction_type}"] = eta_text

    return stops_with_coords, estimated_times

# Selenium 查詢即時站牌資料
def get_bus_route_stops_from_ebus(route_id, bus_name, driver_instance):
    print(f"\n正在從 ebus.gov.taipei 獲取路線 '{bus_name}' ({route_id}) 的站牌數據和到站時間...")

    url = f'https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id}'
    wait = WebDriverWait(driver_instance, 40)

    all_stops_data = []
    all_estimated_times = {}

    try:
        driver_instance.get(url)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'p.stationlist-come-go-c')))
        print("主頁面結構已載入。")

        # 去程
        print("正在獲取去程站牌數據...")
        go_button = driver_instance.find_element(By.CSS_SELECTOR, 'a.stationlist-go')
        go_button.click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#GoDirectionRoute li .auto-list-stationlist-place')))
        try:
            wait.until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#GoDirectionRoute span.eta_onroad'), '分') or
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#GoDirectionRoute span.eta_onroad'), '進站中') or
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#GoDirectionRoute span.auto-list-stationlist-position-time'), '分鐘')
            )
            print("去程到站時間已載入。")
        except Exception as e:
            print(f"警告：去程到站時間等待超時 ({e})，部分或全部到站時間可能未完全載入。")
            time.sleep(5)

        go_page_content = driver_instance.page_source
        go_soup = BeautifulSoup(go_page_content, 'html.parser')
        go_stops, go_estimated_times = extract_stops_from_soup(go_soup, "去程", route_id)
        all_stops_data.extend(go_stops)
        all_estimated_times.update(go_estimated_times)
        print(f"去程數據獲取完成。共 {len(go_stops)} 站。")

        # 返程
        print("正在獲取返程站牌數據...")
        return_button = driver_instance.find_element(By.CSS_SELECTOR, 'a.stationlist-come')
        return_button.click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#BackDirectionRoute li .auto-list-stationlist-place')))
        try:
            wait.until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#BackDirectionRoute span.eta_onroad'), '分') or
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#BackDirectionRoute span.eta_onroad'), '進站中') or
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#BackDirectionRoute span.auto-list-stationlist-position-time'), '分鐘')
            )
            print("返程到站時間已載入。")
        except Exception as e:
            print(f"警告：返程到站時間等待超時 ({e})，部分或全部到站時間可能未完全載入。")
            time.sleep(5)

        return_page_content = driver_instance.page_source
        return_soup = BeautifulSoup(return_page_content, 'html.parser')
        return_stops, return_estimated_times = extract_stops_from_soup(return_soup, "返程", route_id)
        all_stops_data.extend(return_stops)
        all_estimated_times.update(return_estimated_times)
        print(f"返程數據獲取完成。共 {len(return_stops)} 站。")

    except Exception as e:
        print(f"[錯誤] 獲取路線 {bus_name} 站牌數據和到站時間失敗：{e}")
        all_stops_data = []
        all_estimated_times = {}

    print(f"路線 '{bus_name}' 的所有站牌數據和到站時間獲取完成。共 {len(all_stops_data)} 站。")
    return all_stops_data, all_estimated_times

# folium 顯示地圖
def display_bus_route_on_map(route_name, stops_data, bus_location=None, estimated_times=None):
    if not stops_data:
        print(f"沒有路線 '{route_name}' 的站牌數據可顯示。")
        return

    print(f"\n正在為路線 '{route_name}' 生成地圖...")

    go_coords = [[s["lat"], s["lon"]] for s in stops_data if s.get("direction") == "去程"]
    return_coords = [[s["lat"], s["lon"]] for s in stops_data if s.get("direction") == "返程"]

    all_lats = [s["lat"] for s in stops_data]
    all_lons = [s["lon"] for s in stops_data]

    if all_lats and all_lons:
        avg_lat = sum(all_lats) / len(all_lats)
        avg_lon = sum(all_lons) / len(all_lons)
        map_center = [avg_lat, avg_lon]
    else:
        map_center = [25.0330, 121.5654]
        print("警告：未找到站牌經緯度，地圖中心設為台北市中心。")

    m = folium.Map(location=map_center, zoom_start=13)

    colors = {"去程": "red", "返程": "green"}
    line_colors = {"去程": "red", "返程": "green"}

    for stop in stops_data:
        stop_name = stop["name"]
        coords = [stop["lat"], stop["lon"]]
        direction = stop.get("direction", "未知方向")
        est_time_key = f"{stop_name}_{direction}"
        est_time_text = estimated_times.get(est_time_key, "查無資訊") if estimated_times else "查無資訊"
        popup_html = f"<b>{stop_name}</b><br>方向: {direction}<br>預估時間: {est_time_text}"

        folium.Marker(
            location=coords,
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=colors.get(direction, "gray"), icon="info-sign")
        ).add_to(m)

    if go_coords and len(go_coords) > 1:
        folium.PolyLine(
            locations=go_coords,
            color=line_colors.get("去程"),
            weight=5,
            opacity=0.7,
            tooltip=f"路線: {route_name} (去程)"
        ).add_to(m)

    if return_coords and len(return_coords) > 1:
        folium.PolyLine(
            locations=return_coords,
            color=line_colors.get("返程"),
            weight=5,
            opacity=0.7,
            tooltip=f"路線: {route_name} (返程)"
        ).add_to(m)

    if bus_location:
        folium.Marker(
            location=[bus_location["lat"], bus_location["lon"]],
            popup=folium.Popup(f"<b>公車位置</b><br>路線: {route_name}", max_width=200),
            icon=folium.Icon(color="red", icon="bus", prefix="fa")
        ).add_to(m)

    map_filename = f"bus_route_{route_name}_map.html"
    m.save(map_filename)
    print(f"地圖已保存到 '{map_filename}'。")
    print("正在嘗試在瀏覽器中打開地圖...")
    webbrowser.open(map_filename)
    print("✅ 完成！")

if __name__ == "__main__":
    print("歡迎使用台北市公車路線查詢與地圖顯示工具！")
    print("-----------------------------------")

    # 1. 讀取本地 bus_data.csv
    bus_info_path = r"C:\Users\User\Desktop\cycu_oop_11022101\bus_data.csv"
    all_routes = {}
    with open(bus_info_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            route = row['route_name']
            stop = row['stop_name']
            if route not in all_routes:
                all_routes[route] = []
            all_routes[route].append(stop)

    # 2. 使用者輸入出發站與目的站
    start_stop = input("請輸入出發站名稱：").strip()
    end_stop = input("請輸入目的站名稱：").strip()

    # 3. 查詢可搭乘之公車路線
    possible_routes = []
    for route, stops in all_routes.items():
        if start_stop in stops and end_stop in stops:
            possible_routes.append(route)

    if not possible_routes:
        print("查無同時經過出發站與目的站的公車路線。")
        exit()

    print("\n可搭乘的公車路線：")
    for idx, route in enumerate(possible_routes):
        print(f"{idx+1}. {route}")

    selected_idx = int(input("請輸入要查詢的路線編號：")) - 1
    selected_route_name = possible_routes[selected_idx]

    # 3. 顯示該路線所有站點資訊
    print(f"\n路線「{selected_route_name}」所有站點：")
    for idx, stop in enumerate(all_routes[selected_route_name]):
        print(f"{idx+1}. {stop}")

    # 4. 啟動 Selenium，只查詢使用者選定的路線即時到站時間
    print("\n正在啟動 Chrome WebDriver 並查詢即時到站時間...")
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.page_load_strategy = 'normal'
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    chrome_options.add_argument("--log-level=OFF")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        print("WebDriver 已啟動。")

        # 取得 route_id
        route_id = None
        driver.get("https://ebus.gov.taipei/ebus")
        wait_initial = WebDriverWait(driver, 30)
        wait_initial.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-toggle='collapse'][href*='#collapse']")))
        time.sleep(2)
        for i in range(1, 23):
            try:
                collapse_link_selector = f"a[href='#collapse{i}']"
                collapse_link = driver.find_element(By.CSS_SELECTOR, collapse_link_selector)
                if collapse_link.get_attribute("aria-expanded") == "false" or "collapsed" in collapse_link.get_attribute("class"):
                    driver.execute_script("arguments[0].click();", collapse_link)
                    time.sleep(0.5)
            except Exception:
                pass
        time.sleep(3)
        bus_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='javascript:go']")
        for link in bus_links:
            href = link.get_attribute("href")
            name = link.text.strip()
            if name == selected_route_name:
                route_id_match = re.search(r"go\('([^']+)'\)", href)
                if route_id_match:
                    route_id = route_id_match.group(1)
                    break

        if not route_id:
            print("找不到該路線的 route_id，無法查詢即時資訊。")
            driver.quit()
            exit()

        # 5. 查詢即時到站時間並顯示地圖
        stops_with_coords, estimated_times_data = get_bus_route_stops_from_ebus(route_id, selected_route_name, driver)
        display_bus_route_on_map(selected_route_name, stops_with_coords, None, estimated_times_data)

    except Exception as e:
        print(f"錯誤：{e}")
    finally:
        if driver:
            driver.quit()
        print("WebDriver 已關閉。")