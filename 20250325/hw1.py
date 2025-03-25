import pandas as pd
import matplotlib.pyplot as plt

df=pd.read_csv('ExchangeRate@202503251855.csv')

df['sum']=df['x']+df['y']

print(df['sum'])

plt.scatter(df['x'],df['y'])
plt.xlabel('x')
plt.ylabel('y')
plt.title('Scatter plot of x and y')
plt.show()