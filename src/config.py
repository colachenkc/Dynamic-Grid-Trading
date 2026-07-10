symbol = "BTCUSDT_spot"
start_time = "2021-01-01 00:00:00"
end_time   = "2024-07-31 23:59:00"

grid_sizes = [0.005, 0.01, 0.015, 0.02, 0.03, 0.05, 0.07, 0.1]
grid_numbers_half_list = [2, 3, 5, 7, 10]

grid_principal = 100
fee_pct = 0.0008
# Set to (grid_size, grid_numbers_half) to run only that config and dump every
# fill to CSV for charting. None = normal full sweep, no trade log.
trade_log = None

# Symmetric inventory: sell back the coin bought by the last down-break when
# price breaks up again. False = the paper (coin is never sold).
sell_on_up_break = False
