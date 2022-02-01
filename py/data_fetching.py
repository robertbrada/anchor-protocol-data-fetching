from terra_sdk.client.lcd import AsyncLCDClient
from prometheus_client import (Gauge)
import asyncio

# Contract addresses (https://docs.anchorprotocol.com/smart-contracts/deployed-contracts)
ANCHOR_MARKET_ADDRESS = "terra1sepfj7s0aeg5967uxnfk4thzlerrsktkpelm5s"
ANCHOR_ORACLE_ADDRESS = "terra1cgg6yef7qcdm070qftghfulaxmllgmvk77nc7t"
ANCHOR_BLUNA_CUSTODY_ADDRESS = "terra1ptjp2vfjrwh0j0faj9r6katm640kgjxnwwq9kn"
ANCHOR_BETH_CUSTODY_ADDRESS = "terra10cxuzggyvvv44magvrh3thpdnk9cmlgk93gmx2"
BLUNA_ADDRESS = "terra1kc87mu460fwkqte29rquh4hc20m54fxwtsx7gp"
BETH_ADDRESS = "terra1dzhzukyezv0etz22ud940z7adyv7xgcjkahuun"

# Connect to columbus network
terra = AsyncLCDClient(url="https://lcd.terra.dev", chain_id="columbus-5")


async def getTotalDepositUSD():
    # query data about Anchors's Market-Contract current state
    response = await terra.wasm.contract_query(ANCHOR_MARKET_ADDRESS, {
        "state": {},
    })

    aterra_supply = float(response["prev_aterra_supply"])
    # aUST token Total Supply
    exchange_rate = float(response["prev_exchange_rate"])

    # divide by 10**6 in order to get the right USD value
    # aUST has 6 decimals: https: // finder.terra.money/columbus-4/address/terra1hzh9vpxhsk8253se0vv5jj6etdvxu3nv8z07zu
    return (aterra_supply / 10 ** 6) * exchange_rate


async def getBTokenCollateralUSD(bTokenAddress, bTokenAnchorCustodyAddress):
    # Query bToken contract how much of it is bTokenAnchorCustody contract holding
    balanceResponse = await terra.wasm.contract_query(bTokenAddress, {
        "balance": {"address": bTokenAnchorCustodyAddress},
    })
    bTokenBalance = float(balanceResponse["balance"])

    # get price usd price of given bToken
    priceResponse = await terra.wasm.contract_query(ANCHOR_ORACLE_ADDRESS, {
        "price": {
            "base": bTokenAddress,
            "quote": "uusd",
        },
    })
    bTokenPrice = float(priceResponse["rate"])

    # get token decimals ( in order to compute corresponding USD value properly)
    tokenInfoResponse = await terra.wasm.contract_query(bTokenAddress, {
        "token_info": {},
    })
    tokenDecimals = tokenInfoResponse["decimals"]

    # return total collateral for the given bToken
    return bTokenPrice * (bTokenBalance / 10 ** tokenDecimals)


async def getTotalCollateralUSD(bTokenAddresses: list, bTokenAnchorCustodyAddresses: list):
    totalCollateralUSD = 0

    for i in range(len(bTokenAddresses)):
        collateral = await getBTokenCollateralUSD(bTokenAddresses[i], bTokenAnchorCustodyAddresses[i])
        totalCollateralUSD += collateral

    return totalCollateralUSD

def formatToPrometheus(tvl, total_deposit, total_collateral):
    # This is expected:
    return ("\n# HELP tvl_usd Total USD value locked (collateral + deposit)\n"
    "# TYPE tvl_usd gauge\n"
    "tvl_usd {tvl}\n"
    "# HELP total_deposit_usd USD of all deposits\n"
    "# TYPE total_deposit_usd gauge\n"
    "total_deposit_usd {deposit}\n"
    "# HELP total_collateral_usd USD of all collaterals\n"
    "# TYPE total_collateral_usd gauge\n"
    "total_collateral_usd {collateral}\n").format(tvl=tvl, deposit=total_deposit, collateral=total_collateral)

async def main():
    totalDepositUSD = await getTotalDepositUSD()
    collateralBLunaUSD = await getBTokenCollateralUSD(
        BLUNA_ADDRESS,
        ANCHOR_BLUNA_CUSTODY_ADDRESS
    )
    collateralBEthUSD = await getBTokenCollateralUSD(
        BETH_ADDRESS,
        ANCHOR_BETH_CUSTODY_ADDRESS
    )

    totalCollateralUSD = collateralBLunaUSD + collateralBEthUSD

    # print("-------------------------------------------")
    # print("TVL", totalDepositUSD + totalCollateralUSD, "USD")
    # print("totalDeposit", totalDepositUSD, "USD")
    # print("totalCollateral", totalCollateralUSD, "USD")
    # print("collateralBLuna", collateralBLunaUSD, "USD")
    # print("collateralBEth", collateralBEthUSD, "USD")
    # print("-------------------------------------------")

    # print in format the Prometheus expects
    print(formatToPrometheus(totalDepositUSD + totalCollateralUSD, totalDepositUSD, totalCollateralUSD))

# uncomment to run the async main function
asyncio.get_event_loop().run_until_complete(main())
