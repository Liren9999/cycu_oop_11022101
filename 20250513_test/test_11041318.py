from m11041318.ebus_map import get_bus_info_go

if __name__ == "__main__":
    # 測試 get_bus_info_go 函式
    stop_info = get_bus_info_go('0161000900')
    print(f"Route Info Go: {stop_info}")