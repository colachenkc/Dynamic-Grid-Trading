from src.config import grid_principal, fee_pct

def calculate_grid_levels(start_price, grid_size, grid_numbers_half):
    # delta = mid * grid_size
    delta = start_price * grid_size

    levels = [start_price - delta * i for i in range(grid_numbers_half, 0, -1)]
    levels.append(start_price)
    levels += [start_price + delta * i for i in range(1, grid_numbers_half + 1)]
    return levels

def calculate_profit_up(grid_numbers, grid_numbers_half, grid_size):
    return (grid_numbers_half * (grid_numbers_half + 1) / 2) * grid_principal / grid_numbers * (grid_size - fee_pct * 2)

def calculate_profit_down(grid_numbers, k, grid_size):
    return (k * (k + 1) / 2) * grid_principal / grid_numbers * (grid_size - fee_pct * 2)

def calculate_profit_arb_up(grid_numbers, grid_numbers_half, grid_size, trade_count):
    return (trade_count - grid_numbers_half) / 2 * grid_principal / grid_numbers * (grid_size - fee_pct * 2)

def calculate_profit_arb_down(grid_numbers, grid_numbers_half, grid_size, trade_count, count):
    return (trade_count - grid_numbers_half - count) / 2 * grid_principal / grid_numbers * (grid_size - fee_pct * 2)

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
    profit_arb = calculate_profit_arb_up(grid_numbers, grid_numbers_half, grid_size, trade_count)

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
    max_price, grid_levels, initial_price, fee_pct
):
    count = 0
    for i in range(1, grid_numbers_half):
        if max_price >= grid_levels[grid_numbers_half + i]:
            count += 1
        else:
            break
    profit_down = calculate_profit_down(grid_numbers, count, grid_size) # 上漲收益
    profit_arb = calculate_profit_arb_down(grid_numbers, grid_numbers_half, grid_size, trade_count, count) # 套利收益

    USDT += profit_down + profit_arb
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
    max_price,
    trade_count,
    grid_numbers_half,
    grid_numbers,
    grid_principal,
    grid_size,
    fee_pct,
    USDT,
    COIN,
):
    # 根據 max_price 計算上漲方向利潤
    count_up = 0
    for i in range(1, grid_numbers_half):
        if max_price >= grid_levels[grid_numbers_half + i]:
            count_up += 1
        else:
            break
    profit_up = calculate_profit_up(grid_numbers, count_up, grid_size)

    # 計算買入的COIN
    count_down = 0
    coin_from_buys = 0.0
    unused_cash = 0.0
    for i in range(grid_numbers_half):
        if grid_levels[i] >= close_price:
            coin_from_buys += (grid_principal / grid_numbers / grid_levels[i] * (1 - fee_pct * 2))
            count_down += 1
        else:
            unused_cash += grid_principal / grid_numbers

    # 套利收益
    arb_cycles = (trade_count - count_up - count_down) / 2
    profit_arb = (arb_cycles * grid_principal / grid_numbers * (grid_size - fee_pct * 2))

    USDT += profit_up + profit_arb + unused_cash
    COIN += coin_from_buys

    return USDT, COIN