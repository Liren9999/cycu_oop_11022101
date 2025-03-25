import requests
from bs4 import BeautifulSoup

def fetch_bus_schedule(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # 根據網站的 HTML 結構解析資料
        schedule = {}
        # 假設每個車站和到站時間在一個 <div class="station"> 和 <div class="time"> 中
        stations = soup.find_all('div', class_='station')
        times = soup.find_all('div', class_='time')
        for station, time in zip(stations, times):
            station_name = station.text.strip()
            arrival_time = int(time.text.strip().replace('分鐘', ''))
            schedule[station_name] = arrival_time
        return schedule
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None

def get_arrival_time(station_name, schedule):
    """
    根據車站名稱顯示到站時間

    :param station_name: 車站名稱
    :param schedule: 包含車站名稱和到站時間的字典
    :return: 到站時間或錯誤訊息
    """
    if station_name in schedule:
        return f"{station_name} 的下一班車將在 {schedule[station_name]} 分鐘後到達。"
    else:
        return f"找不到車站 {station_name} 的到站時間。"

# 使用範例
url = 'https://pda5284.gov.taipei/MQS/route.jsp?rid=10417'
schedule = fetch_bus_schedule(url)
if schedule:
    station_name = "站B"  # 替換為你要查詢的車站名稱
    print(get_arrival_time(station_name, schedule))