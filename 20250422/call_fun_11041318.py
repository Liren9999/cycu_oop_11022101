# call_function.py
from bus_info_11022101 import bus_info  # 导入 bus_info 函数

def main():
    # 让用户输入公车代号和方向
    routeid = input("请输入公车代号（例如: 0100000A00）: ").strip()
    direction = input("请输入方向（'go' 或 'come'）: ").strip()

    # 调用 bus_info 函数并获取输出
    output = bus_info(routeid, direction)

    # 输出结果
    print(output)

if __name__ == "__main__":
    main()
