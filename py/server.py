from prometheus_client import (Gauge, start_http_server)

# Create a metric to track time spent and requests made.
TOTAL_VALUE_LOCKED = Gauge('tvl_usd', 'Total USD value locked (collateral + deposit)')
TOTAL_DEPOSIT = Gauge('total_deposit_usd', 'USD value of all deposits')
TOTAL_COLLATERAL = Gauge('total_collateral_usd', 'USD value of all collaterals')

def process_tvl():
    # TODO how to load async data?
    # tvl = await getTvlUSD()
    tvl = 1.0
    TOTAL_VALUE_LOCKED.set(tvl) 

def process_deposit():
    # TODO how to load async data?
    # deposit = await getTotalDepositUSD()
    deposit = 2.0
    TOTAL_DEPOSIT.set(deposit) 

def process_collateral():
    # TODO how to load async data?
    # collateral = await getTotalCollateralUSD()
    collateral = 3.0
    TOTAL_COLLATERAL.set(collateral) 


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)

    # Generate some requests.
    while True:
        process_tvl()
        process_collateral()
        process_deposit()
