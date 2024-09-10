import pandas as pd
import numpy as np

symbol = 'BTCUSDT_spot'

df = pd.read_csv(f'{symbol}_1m.csv')

df['Open Time'] = pd.to_datetime(df['Open Time'])

start_time = '2021-01-01 00:00:00'
end_time = '2024-07-31 23:59:00'

df = df[(df['Open Time'] >= start_time) & (df['Open Time'] <= end_time)]

grid_sizes = [0.005, 0.01, 0.015, 0.02, 0.03, 0.05, 0.07, 0.1]
grid_numbers_half_list = [2, 3, 5, 7, 10]
fee_pct = 0.0008

def calculate_grid_levels(start_price, grid_size, grid_numbers_half):
    levels = [start_price / (1 + grid_size)**i for i in range(grid_numbers_half, 0, -1)]
    levels.append(start_price)
    levels += [start_price * (1 + grid_size)**i for i in range(1, grid_numbers_half + 1)]
    return levels

results = []

for grid_size in grid_sizes:
    for grid_numbers_half in grid_numbers_half_list:
        wallet = 0
        money_input = 100
        grid_numbers = 2 * grid_numbers_half 

        initial_price = df.iloc[0]['Open']

        grid_levels = calculate_grid_levels(initial_price, grid_size, grid_numbers_half)
        lower_bound = grid_levels[0]
        upper_bound = grid_levels[-1]
        current_level = grid_levels.index(initial_price)
        max_price = initial_price
        min_price = initial_price
        print(f"Starting a new grid with middle: {initial_price}")

        trade_count = 0

        USDT = 0
        BTC = 0

        row_count = 0
        grid_count = 1
        for index, row in df.iterrows():
            prices = [row['Open'], row['Low'], row['High'], row['Close']]

            if row_count != 0:
                prices[0] = prev
            
            for i in range(len(prices) - 1):
                start_price = prices[i]
                end_price = prices[i + 1]
                max_price = max(max_price, end_price)
                min_price = min(min_price, end_price)

                if start_price < end_price:
                    while current_level < grid_numbers and start_price <= grid_levels[current_level + 1] < end_price:
                        print(f"Sell at price = {grid_levels[current_level + 1]}")
                        current_level += 1
                        trade_count += 1
                else:
                    while current_level > 0 and end_price <= grid_levels[current_level - 1] < start_price:
                        print(f"Buy at price = {grid_levels[current_level - 1]}")
                        current_level -= 1
                        trade_count += 1

                if end_price > upper_bound:
                    USDT += 100
                    USDT += (grid_numbers_half * (grid_numbers_half + 1) / 2) * 100 / grid_numbers * (grid_size - fee_pct * 2) # 上漲收益
                    USDT += (trade_count - grid_numbers_half) / 2 * 100 / grid_numbers * (grid_size - fee_pct * 2) # 套利收益
                    initial_price = end_price
                    grid_levels = calculate_grid_levels(initial_price, grid_size, grid_numbers_half)
                    lower_bound = grid_levels[0]
                    upper_bound = grid_levels[-1]
                    current_level = grid_levels.index(initial_price)
                    max_price = initial_price
                    min_price = initial_price
                    print(f"目前投入資金: {grid_count * 100}")
                    print(f"目前USDT: {USDT}")
                    print(f"目前BTC: {BTC}")
                    print(f"目前價值: {USDT + BTC * initial_price}")
                    print(f"目前盈虧: {USDT + BTC * initial_price - grid_count * 100}")
                    print(f"Up Exceed: Starting a new grid with middle: {initial_price}")
                    wallet += (grid_numbers_half * (grid_numbers_half + 1) / 2) * 100 / grid_numbers * (grid_size - fee_pct * 2)
                    wallet += (trade_count - grid_numbers_half) / 2 * 100 / grid_numbers * (grid_size - fee_pct * 2)
                    trade_count = 0
                    grid_count += 1
                
                if end_price < lower_bound:
                    count = 0
                    for i in range(1, grid_numbers_half):
                        if max_price >= grid_levels[grid_numbers_half + i]:
                            count += 1
                        else:
                            break
                    USDT += (count * (count + 1)) * 100 / grid_numbers * (grid_size - fee_pct * 2) # 上漲收益 
                    USDT += (trade_count - grid_numbers_half - count) / 2 * 100 / grid_numbers * (grid_size - fee_pct * 2) # 套利收益
                    BTC += 50 / initial_price * (1 - fee_pct * 2)
                    for i in range(grid_numbers_half):
                        BTC += 100 / grid_numbers / grid_levels[i] * (1 - fee_pct * 2)
                    initial_price = end_price
                    grid_levels = calculate_grid_levels(initial_price, grid_size, grid_numbers_half)
                    lower_bound = grid_levels[0]
                    upper_bound = grid_levels[-1]
                    current_level = grid_levels.index(initial_price)
                    max_price = initial_price
                    min_price = initial_price
                    print(f"目前投入資金: {grid_count * 100}")
                    print(f"目前USDT: {USDT}")
                    print(f"目前BTC: {BTC}")
                    print(f"目前價值: {USDT + BTC * initial_price}")
                    print(f"目前盈虧: {USDT + BTC * initial_price - grid_count * 100}")
                    print(f"Down Exceed: Starting a new grid with middle: {initial_price}")
                    wallet += (count * (count + 1)) * 100 / grid_numbers * (grid_size - fee_pct * 2)
                    wallet += (trade_count - grid_numbers_half - count) / 2 * 100 / grid_numbers * (grid_size - fee_pct * 2)
                    if wallet >= 100 :
                        wallet -= 100
                    elif wallet < 100 :
                        money_input += 100 - wallet
                        wallet = 0
                    
                    trade_count = 0
                    grid_count += 1

            prev = row['Close']
            row_count += 1

        close_price = df.iloc[len(df)-1]['Close']
        count = 0
        for i in range(1, grid_numbers_half):
            if max_price >= grid_levels[grid_numbers_half + i]:
                count += 1
            else:
                break
        USDT += (count * (count + 1)) * 100 / grid_numbers * (grid_size - fee_pct * 2) # 上漲收益
        count2 = 0
        for i in range(grid_numbers_half):
            if grid_levels[i] >= close_price:
                BTC += 100 / grid_numbers / grid_levels[i] * (1 - fee_pct * 2)
                count2 += 1
        USDT += (trade_count - count - count2) / 2 * 100 / grid_numbers * (grid_size - fee_pct * 2) # 套利收益
        USDT += (grid_numbers_half - count2) * 100 / grid_numbers
        
        summary = {
            'grid_size': grid_size,
            'grid_numbers_half': grid_numbers_half,
            'money': grid_count * 100,
            'USDT': USDT,
            'BTC': BTC,
            'total_value': USDT + BTC * close_price,
            'profit': USDT + BTC * close_price - grid_count * 100,
            'profit_percentage': (USDT + BTC * close_price) / (grid_count * 100) * 100 - 100,
            'USDT_profit_percentage': USDT / (grid_count * 100) * 100 - 100,
            'input money': money_input,
            'real_profit_percentage': (USDT + BTC * close_price) / money_input * 100 - 100,
            'real_USDT_profit_percentage': USDT / money_input * 100 - 100,
            'IRR': ((USDT + BTC * close_price) / money_input) ** (12 / 43) * 100 - 100 
        }
        
        results.append(summary)
        print("Summary:======================================================================================")
        print(f"目前投入資金: {grid_count * 100}")
        print(f"目前USDT: {USDT}")
        print(f"目前BTC: {BTC}")
        print(f"目前價值: {USDT + BTC * close_price}")
        print(f"目前盈虧: {USDT + BTC * close_price - grid_count * 100}")
        print(f"收益率: {(USDT + BTC * close_price) / (grid_count * 100) * 100 - 100}%")
        print(f"USDT收益率: {USDT / (grid_count * 100) * 100 - 100}%")

results_df = pd.DataFrame(results)
results_df.to_csv(f'{symbol}_grid_strategy_backtest_results.csv', index=False)

print("Results saved to grid_trading_results.csv")
