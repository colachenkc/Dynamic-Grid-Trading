import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

symbol = 'BTCUSDT_spot'
df = pd.read_csv(f'{symbol}_1m.csv')

df['Open Time'] = pd.to_datetime(df['Open Time'])

start_time = '2021-01-01 00:00:00'
end_time = '2024-07-31 23:59:00'

df = df[(df['Open Time'] >= start_time) & (df['Open Time'] <= end_time)]

lower_bound = 10000
upper_bound = 80000
fee_pct = 0.0008

results = []

grid_sizes = [round(x, 3) for x in list(np.arange(0.003, 0.101, 0.001))]


Grid_Sizes = []
Profit = []

for grid_size in grid_sizes:
    print(grid_size)
    grid_levels = []
    level = lower_bound
    while level <= upper_bound:
        grid_levels.append(level)
        level *= (1 + grid_size)
    grid_levels.append(level)  

    trade_count = 0

    first_close = df.iloc[0]['Open']
    current_level = 0
    for i in range(len(grid_levels) - 1):
        if grid_levels[i] <= first_close < grid_levels[i + 1]:
            current_level = i
            break


    row_count = 0
    for index, row in df.iterrows():
        prices = [row['Open'], row['Low'], row['High'], row['Close']] # Capitalize
        if row_count != 0:
            prices[0] = prev

        for i in range(len(prices) - 1):
            start_price = prices[i]
            end_price = prices[i + 1]
            if start_price < end_price:
                while True:
                    if start_price <= grid_levels[current_level+1] < end_price:
                        print(grid_levels[current_level+i])
                        current_level += 1
                        trade_count += 1
                    else:
                        break
            else:
                while True:
                    if end_price <= grid_levels[current_level-1] < start_price:
                        print(grid_levels[current_level-1])
                        current_level -= 1
                        trade_count += 1
                    else:
                        break

        prev = row['Close']
        row_count += 1

    fake_count = 0
    open_price = df.iloc[0]['Open']
    close_price = df.iloc[len(df)-1]['Close']
    if open_price < close_price:
        for level in grid_levels:
            if open_price <= level < close_price:
                fake_count += 1
    else:
        for level in grid_levels:
            if close_price <= level < open_price:
                fake_count += 1

    key_num = (trade_count - fake_count) / 2
    profit_per_grid = 100 / (len(grid_levels)-1) * (grid_size - fee_pct * 2) * key_num # -1

    Grid_Sizes.append(grid_size)
    Profit.append(profit_per_grid)
    results.append({
        'grid_size': grid_size,
        'grid_count': len(grid_levels)-1, 
        'trade_count': trade_count,
        'fake_count': fake_count,
        'arbitrage number': key_num,
        'profit from arbitrage': profit_per_grid
    })

results_df = pd.DataFrame(results)
results_df.to_csv(f'{symbol}_exp1.csv', index=False)
plt.plot(Grid_Sizes, Profit, 'red')
plt.xlabel('Grid Size')
plt.ylabel('Profit per Grid')
plt.title('Grid & Profit')
plt.show()