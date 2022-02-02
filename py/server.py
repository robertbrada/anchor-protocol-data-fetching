#!/usr/bin/env python
"""
This example demonstrates how the ``aioprometheus.Service`` can be used to
expose metrics on a HTTP endpoint.

Build according to this tutorial: https://github.com/claws/aioprometheus
"""

import asyncio

from aioprometheus import Gauge
from aioprometheus.service import Service
from terra_sdk.client.lcd import AsyncLCDClient

from data_fetching import getTotalCollateralUSD, getTotalDepositUSD

# Contract addresses (https://docs.anchorprotocol.com/smart-contracts/deployed-contracts)
ANCHOR_MARKET_ADDRESS = "terra1sepfj7s0aeg5967uxnfk4thzlerrsktkpelm5s"
ANCHOR_ORACLE_ADDRESS = "terra1cgg6yef7qcdm070qftghfulaxmllgmvk77nc7t"
ANCHOR_BLUNA_CUSTODY_ADDRESS = "terra1ptjp2vfjrwh0j0faj9r6katm640kgjxnwwq9kn"
ANCHOR_BETH_CUSTODY_ADDRESS = "terra10cxuzggyvvv44magvrh3thpdnk9cmlgk93gmx2"
BLUNA_ADDRESS = "terra1kc87mu460fwkqte29rquh4hc20m54fxwtsx7gp"
BETH_ADDRESS = "terra1dzhzukyezv0etz22ud940z7adyv7xgcjkahuun"

async def main():

    service = Service()

    # Create metrics
    # You can add optional labels like this: 
    # TOTAL_DEPOSIT = Gauge('total_deposit_usd', 'USD value of all deposits', const_labels={"host": socket.gethostname()})
    TOTAL_VALUE_LOCKED = Gauge('tvl_usd', 'Total USD value locked (collateral + deposit)')
    TOTAL_DEPOSIT = Gauge('total_deposit_usd', 'USD value of all deposits')
    TOTAL_COLLATERAL = Gauge('total_collateral_usd', 'USD value of all collaterals')

    # Initialize terra client
    terra = AsyncLCDClient(url="https://lcd.terra.dev", chain_id="columbus-5")

    await service.start(addr="127.0.0.1", port=8000)
    print(f"Serving prometheus metrics on: {service.metrics_url}")

    # Now start another coroutine to periodically update a metric to
    # simulate the application making some progress.
    async def updater(tvlG: Gauge, depositG: Gauge, collateralG: Gauge):
        while True:
            totalDepositUSD = await getTotalDepositUSD(terra, ANCHOR_MARKET_ADDRESS)
            totalCollateralUSD = await getTotalCollateralUSD(
                terra, 
                [BLUNA_ADDRESS, BETH_ADDRESS], 
                [ANCHOR_BLUNA_CUSTODY_ADDRESS, ANCHOR_BETH_CUSTODY_ADDRESS])

            # set the gauge values
            depositG.set({}, totalDepositUSD)
            collateralG.set({}, totalCollateralUSD)
            tvlG.set({}, totalCollateralUSD + totalDepositUSD)

    await updater(TOTAL_VALUE_LOCKED, TOTAL_DEPOSIT, TOTAL_COLLATERAL)

    # Finally stop server
    await service.stop()


if __name__ == "__main__":

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
