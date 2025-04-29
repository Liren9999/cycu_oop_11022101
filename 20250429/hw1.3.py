from PIL import Image

# 圖片路徑
icon_path = r"C:\Users\User\Desktop\cycu_oop_11022101\data\person_icon.png"

# 檢查圖片是否存在
if not os.path.exists(icon_path):
    print(f"❌ 找不到圖片：{icon_path}")
else:
    # 開啟圖片
    img = Image.open(icon_path)
    # 獲取圖片尺寸
    width, height = img.size
    print(f"圖片的像素大小為：{width}x{height}")