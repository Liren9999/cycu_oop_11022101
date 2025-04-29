# -*- coding: utf-8 -*-
import os
import csv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time


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
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.url)
            
            # 根據方向選擇去程或返程
            if self.direction == 'come':
                page.click('a.stationlist-come')  # 點擊返程按鈕
            elif self.direction == 'go':
                page.click('a.stationlist-go')  # 點擊去程按鈕
            
            try:
                # 等待站點資訊載入完成
                page.wait_for_selector('.auto-list-stationlist', timeout=10000)  # 最多等待 10 秒
                # 模擬等待更多時間以確保動態更新完成
                time.sleep(5)  # 等待 5 秒
                self.content = page.content()
            except Exception as e:
                print(f"等待目標元素時發生錯誤: {e}")
                self.content = None
            finally:
                browser.close()

        # 儲存 HTML 內容到檔案（除錯用）
        os.makedirs("data", exist_ok=True)  # 確保資料夾存在
        with open(f"data/ebus_taipei_{self.rid}_{self.direction}.html", "w", encoding="utf-8") as file:
            file.write(self.content or "")

    def _parse_and_save_to_csv(self):
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(self.content, 'html.parser') if self.content else None
        stops = []

        if not soup:
            return "無法解析 HTML 內容，請檢查網頁結構或連線問題。"

        # 根據提供的 HTML 結構，選擇站點資訊
        stop_elements = soup.select('.auto-list-stationlist')  # 修改選擇器以符合實際網站結構
        if not stop_elements:
            return "無法找到站點資訊，請檢查選擇器或網站結構。"

        for stop in stop_elements:
            try:
                # 提取到站時間
                arrival_info_element = stop.select_one('.auto-list-stationlist-position-now')  # 提取進站中
                if arrival_info_element:
                    arrival_info = arrival_info_element.text.strip()
                else:
                    arrival_info_element = stop.select_one('.auto-list-stationlist-position-time')  # 提取數字時間
                    if arrival_info_element:
                        arrival_info = arrival_info_element.text.strip()
                    else:
                        arrival_info_element = stop.select_one('.auto-list-stationlist-position-none')  # 提取尚未發車
                        arrival_info = arrival_info_element.text.strip() if arrival_info_element else "尚未發車"

                stop_number = stop.select_one('.auto-list-stationlist-number').text.strip()  # 車站序號
                stop_name = stop.select_one('.auto-list-stationlist-place').text.strip()  # 車站名稱
                stop_id = stop.select_one('input[name="item.UniStopId"]')['value']  # 車站編號
                latitude = stop.select_one('input[name="item.Latitude"]')['value']  # 緯度
                longitude = stop.select_one('input[name="item.Longitude"]')['value']  # 經度

                stops.append([arrival_info, stop_number, stop_name, stop_id, latitude, longitude])
            except AttributeError:
                # 遇到錯誤時，跳過該車站
                print("無法提取某些資訊，跳過該車站")
                continue

        # 確保資料夾存在
        os.makedirs("data", exist_ok=True)

        # 將資料寫入 CSV
        csv_filename = f"data/bus_route_{self.rid}_{self.direction}.csv"
        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["arrival_info", "stop_number", "stop_name", "stop_id", "latitude", "longitude"])
            writer.writerows(stops)

        output = [f"資料已儲存至 {csv_filename}"]
        for stop in stops:
            output.append(f"公車到達時間: {stop[0]}, 車站序號: {stop[1]}, 車站名稱: {stop[2]}, 車站編號: {stop[3]}, 緯度: {stop[4]}, 經度: {stop[5]}")

        return "\n".join(output)


def bus_info(routeid: str, direction: str = 'go') -> str:
    """
    呼叫 BusRouteInfo 類別並返回其輸出內容。
    """
    try:
        route = BusRouteInfo(routeid=routeid, direction=direction)
        return route.output
    except ValueError as e:
        return f"輸入錯誤: {e}"
    except Exception as e:
        return f"發生錯誤: {e}"


if __name__ == "__main__":
    # 讓使用者輸入公車代碼和方向
    routeid = input("請輸入公車代碼 (例如: 0100000A00): ").strip()
    direction = input("請輸入方向 ('go' 或 'come'): ").strip()

    output = bus_info(routeid, direction)
    print(output)