import pandas as pd
import numpy as np

from src.config import (
    symbol, start_time, end_time,
    grid_sizes, grid_numbers_half_list,
    grid_principal, fee_pct,
)
from src.grid_logic import (
    reset_grid, handle_up_break, handle_down_break,
    settle_last_grid_segment, print_current_status,
)

df = pd.read_csv(f"{symbol}_1m.csv")
df["Open Time"] = pd.to_datetime(df["Open Time"])
df = df[(df["Open Time"] >= start_time) & (df["Open Time"] <= end_time)]

results = []

for grid_size in grid_sizes:
    for grid_numbers_half in grid_numbers_half_list:
        USDT = 0.0
        COIN = 0.0
        row_count = 0
        trade_count = 0
        money_input = grid_principal
        grid_numbers = 2 * grid_numbers_half 
        grid_count = 1

        initial_price = df.iloc[0]['Open']
        print(f"Starting a new grid with middle: {initial_price}")
        grid_levels, lower_bound, upper_bound, current_level = \
            reset_grid(initial_price, grid_size, grid_numbers_half)
        max_price = min_price = initial_price


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

                if end_price > upper_bound or current_level == grid_numbers:
                    USDT, grid_count, money_input, trade_count = \
                    handle_up_break(
                        grid_numbers, grid_numbers_half, grid_size, 
                        grid_principal, trade_count, USDT, grid_count, money_input
                    )
                    initial_price = end_price
                    grid_levels, lower_bound, upper_bound, current_level = \
                        reset_grid(initial_price, grid_size, grid_numbers_half)
                    max_price = min_price = initial_price

                    print_current_status(USDT, COIN, initial_price, money_input)
                    print(f"Up Exceed: Starting a new grid with middle: {initial_price}")
                
                if end_price < lower_bound or current_level == 0:
                    USDT, COIN, grid_count, money_input, trade_count = \
                    handle_down_break(
                        grid_numbers, grid_numbers_half, grid_size,
                        grid_principal, trade_count,
                        USDT, COIN, grid_count, money_input,
                        max_price, grid_levels, initial_price, fee_pct,
                    )

                    initial_price = end_price
                    grid_levels, lower_bound, upper_bound, current_level = \
                        reset_grid(initial_price, grid_size, grid_numbers_half)
                    max_price = min_price = initial_price

                    print_current_status(USDT, COIN, initial_price, money_input)

                    print(f"Down Exceed: Starting a new grid with middle: {initial_price}")

            prev = row['Close']
            row_count += 1

        close_price = df.iloc[len(df)-1]['Close']
        USDT, COIN = settle_last_grid_segment(
            close_price=close_price,
            grid_levels=grid_levels,
            max_price=max_price,
            trade_count=trade_count,
            grid_numbers_half=grid_numbers_half,
            grid_numbers=grid_numbers,
            grid_principal=grid_principal,
            grid_size=grid_size,
            fee_pct=fee_pct,
            USDT=USDT,
            COIN=COIN,
        )
        
        summary = {
            'grid_size': grid_size,
            'grid_numbers_half': grid_numbers_half,
            'USDT': USDT,
            'COIN': COIN,
            'total_value': USDT + COIN * close_price,
            'profit': USDT + COIN * close_price - money_input,
            'USDT_profit_percentage': USDT / (money_input) * 100 - 100,
            'input money': money_input,
            'real_profit_percentage': (USDT + COIN * close_price) / money_input * 100 - 100,
            'real_USDT_profit_percentage': USDT / money_input * 100 - 100,
            'IRR': ((USDT + COIN * close_price) / money_input) ** (12 / 43) * 100 - 100   # You can adjust the parameters based on the interval
        }
        
        results.append(summary)
        print("Summary:======================================================================================")
        print_current_status(USDT, COIN, initial_price, money_input)

results_df = pd.DataFrame(results)
results_df.to_csv(f'{symbol}_grid_strategy_backtest_results.csv', index=False)

print("Results saved to grid_trading_results.csv")