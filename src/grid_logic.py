from src.config import grid_principal, fee_pct
from bisect import bisect_right

def calculate_grid_levels(start_price, grid_size, grid_numbers_half):
    # delta = mid * grid_size
    delta = start_price * grid_size

    levels = [start_price - delta * i for i in range(grid_numbers_half, 0, -1)]
    levels.append(start_price)
    levels += [start_price + delta * i for i in range(1, grid_numbers_half + 1)]
    return levels

def calculate_profit_up(grid_numbers, grid_numbers_half, grid_size):
    return (grid_numbers_half * (grid_numbers_half + 1) / 2) * (grid_principal / grid_numbers) * (grid_size - fee_pct * 2)

def calculate_profit_down(grid_numbers, k, grid_size):
    return (k * (k + 1) / 2) * (grid_principal / grid_numbers) * (grid_size - fee_pct * 2)

def calculate_profit_arb(grid_numbers, grid_numbers_half, grid_size, trade_count):
    return ((trade_count - grid_numbers_half) / 2) * (grid_principal / grid_numbers) * (grid_size - fee_pct * 2)

def fund_next_grid(USDT, money_input, grid_principal):
    if USDT >= grid_principal:
        # 完全用利潤繼續開新網格
        USDT -= grid_principal
    else:
        # 利潤不夠，補外部本金
        need = grid_principal - USDT
        money_input += need
        USDT = 0
    return USDT, money_input

def reset_grid(initial_price, grid_size, grid_numbers_half):
    grid_levels  = calculate_grid_levels(initial_price, grid_size, grid_numbers_half)
    lower_bound  = grid_levels[0]
    upper_bound  = grid_levels[-1]
    current_lvl  = grid_levels.index(initial_price)
    return grid_levels, lower_bound, upper_bound, current_lvl

def handle_up_break(
    grid_numbers, grid_numbers_half, grid_size,
    grid_principal, trade_count,
    USDT, grid_count, money_input
):
    profit_up  = calculate_profit_up(grid_numbers, grid_numbers_half, grid_size)
    profit_arb = calculate_profit_arb(grid_numbers, grid_numbers_half, grid_size, trade_count)

    USDT  += profit_up + profit_arb + grid_principal

    grid_count += 1
    trade_count = 0
    USDT, money_input = fund_next_grid(USDT, money_input, grid_principal)

    # 回傳更新後的狀態
    return USDT, grid_count, money_input, trade_count

def handle_down_break(
    grid_numbers, grid_numbers_half, grid_size,
    grid_principal, trade_count,
    USDT, COIN, grid_count, money_input,
    grid_levels, initial_price, fee_pct
):

    profit_arb = calculate_profit_arb(grid_numbers, grid_numbers_half, grid_size, trade_count) # 套利收益

    USDT += profit_arb
    COIN += (grid_principal / 2) / initial_price * (1 - fee_pct * 2)
    for i in range(grid_numbers_half):
        COIN += (grid_principal / grid_numbers) / grid_levels[i] * (1 - fee_pct * 2)

    grid_count += 1
    trade_count = 0
    USDT, money_input = fund_next_grid(USDT, money_input, grid_principal)

    # 回傳更新後的狀態
    return USDT, COIN, grid_count, money_input, trade_count

def print_current_status(USDT, COIN, initial_price, money_input):
    print(f"目前USDT: {USDT}")
    print(f"目前COIN: {COIN}")
    print(f"目前價值: {USDT + COIN * initial_price}")
    print(f"目前盈虧: {USDT + COIN * initial_price - money_input}")

def settle_last_grid_segment(
    close_price,
    grid_levels,
    trade_count,
    grid_numbers_half,
    grid_numbers,
    grid_principal,
    grid_size,
    fee_pct,
    USDT,
    COIN,
):
    assert len(grid_levels) == grid_numbers + 1
    mid_idx = grid_numbers_half
    mid_price = grid_levels[mid_idx]

    per_grid_cash = grid_principal / grid_numbers
    mid_coin = (grid_principal / 2) / mid_price * (1 - fee_pct)
    
    # Find close price pos
    idx = bisect_right(grid_levels, close_price) - 1

    if close_price >= mid_price:
        # unused cash
        remain_count = grid_numbers - idx
        USDT += remain_count * per_grid_cash 

        up_count = max(0, idx - mid_idx)

        profit_up = calculate_profit_up(grid_numbers, up_count, grid_size)
        profit_arb = calculate_profit_arb(grid_numbers, up_count, grid_size, trade_count)
        USDT += up_count * per_grid_cash + profit_up + profit_arb
        COIN += mid_coin * (remain_count / grid_numbers_half)
    else:
        down_count = max(0, mid_idx - idx)
        for j in range(mid_idx - 1, idx, -1):
            COIN += (per_grid_cash / grid_levels[j]) * (1 - fee_pct * 2)
        profit_arb = calculate_profit_arb(grid_numbers, down_count, grid_size, trade_count)
        USDT += profit_arb
        # unused cash
        unused_grids = (grid_numbers_half - down_count) 
        USDT += unused_grids * per_grid_cash
        COIN += mid_coin

    return USDT, COIN
    