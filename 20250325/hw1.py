import pandas as pd
import matplotlib.pyplot as plt

# read csv file using pandas

csv_path = '20250325/ExchangeRate@202503251903.csv'
 
#first row is the header,for its column names

df = pd.read_csv(csv_path)
print(df.columns)

#保留 '資料日期','現金','現金.1' 三個欄位即可

df = df[['資料日期','現金','現金.1']]
print(df.columns.to_list())

#將'資料日期'轉換

#使用 matplotlib.pyplot 繪製折線圖 現金(藍色) 與 現金.1(紅色) 的走勢
plt.plot(df['資料日期'],df['現金'],color='blue',label='現金')
plt.plot(df['資料日期'],df['現金.1'],color='red',label='現金.1')
plt.xlabel('Date')
plt.ylabel('Exchange Rate')
plt.title('Exchange Rate of USD to TWD')
plt.legend()
plt.show()