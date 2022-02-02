from terra_sdk.client.lcd import AsyncLCDClient
import asyncio

# Contract addresses (https://docs.anchorprotocol.com/smart-contracts/deployed-contracts)
ANCHOR_MARKET_ADDRESS = "terra1sepfj7s0aeg5967uxnfk4thzlerrsktkpelm5s"
ANCHOR_ORACLE_ADDRESS = "terra1cgg6yef7qcdm070qftghfulaxmllgmvk77nc7t"
ANCHOR_BLUNA_CUSTODY_ADDRESS = "terra1ptjp2vfjrwh0j0faj9r6katm640kgjxnwwq9kn"
ANCHOR_BETH_CUSTODY_ADDRESS = "terra10cxuzggyvvv44magvrh3thpdnk9cmlgk93gmx2"
BLUNA_ADDRESS = "terra1kc87mu460fwkqte29rquh4hc20m54fxwtsx7gp"
BETH_ADDRESS = "terra1dzhzukyezv0etz22ud940z7adyv7xgcjkahuun"

async def getTotalDepositUSD(terra_client, anchor_market_address):
    """
    Function that computes total deposit in Anchor Protocol

    :param terra_client: Terra LCD Client
    :return number: Total USD value of deposits
    """

    # query data about Anchors's Market-Contract current state
    response = await terra_client.wasm.contract_query(anchor_market_address, {
        "state": {},
    })

    aterra_supply = float(response["prev_aterra_supply"])
    # aUST token Total Supply
    exchange_rate = float(response["prev_exchange_rate"])

    # divide by 10**6 in order to get the right USD value
    # aUST has 6 decimals: https: // finder.terra.money/columbus-4/address/terra1hzh9vpxhsk8253se0vv5jj6etdvxu3nv8z07zu
    return (aterra_supply / 10 ** 6) * exchange_rate


async def getBTokenCollateralUSD(terra_client, bTokenAddress, bTokenAnchorCustodyAddress):
    """
    Function that computes total collateral value for a given bToken (on 28.1.2022 can be either bLUNA or bETH)

    :param terra_client: Terra LCD Client
    :param str bTokenAddress: Address of bToken smart contract address
    :param str bTokenAnchorCustodyAddress: Address of Anchor's custody smart contract related to given bToken
    :return number: USD value of bToken collateral
    """

    # Query bToken contract how much of it is bTokenAnchorCustody contract holding
    balanceResponse = await terra_client.wasm.contract_query(bTokenAddress, {
        "balance": {"address": bTokenAnchorCustodyAddress},
    })
    bTokenBalance = float(balanceResponse["balance"])

    # get price usd price of given bToken
    priceResponse = await terra_client.wasm.contract_query(ANCHOR_ORACLE_ADDRESS, {
        "price": {
            "base": bTokenAddress,
            "quote": "uusd",
        },
    })
    bTokenPrice = float(priceResponse["rate"])

    # get token decimals ( in order to compute corresponding USD value properly)
    tokenInfoResponse = await terra_client.wasm.contract_query(bTokenAddress, {
        "token_info": {},
    })
    tokenDecimals = tokenInfoResponse["decimals"]

    # return total collateral for the given bToken
    return bTokenPrice * (bTokenBalance / 10 ** tokenDecimals)


async def getTotalCollateralUSD(terra_client, bTokenAddresses: list, bTokenAnchorCustodyAddresses: list):
    """
    Function that computes total collateral value for all tokens passed via parameters

    :param terra_client: Terra LCD Client
    :param list bTokenAddresses: Addresses of bToken smart contracts
    :param list bTokenAnchorCustodyAddresses: Addresses of Anchor's custody smart contracts related to bTokens in bTokenAddresses
    :return number: USD value of total collateral
    """

    totalCollateralUSD = 0

    for i in range(len(bTokenAddresses)):
        collateral = await getBTokenCollateralUSD(terra_client, bTokenAddresses[i], bTokenAnchorCustodyAddresses[i])
        totalCollateralUSD += collateral

    return totalCollateralUSD

async def main():
    # Connect to columbus network
    terra = AsyncLCDClient(url="https://lcd.terra.dev", chain_id="columbus-5")

    # Get metrics
    totalDepositUSD = await getTotalDepositUSD(terra, ANCHOR_MARKET_ADDRESS)
    collateralBLunaUSD = await getBTokenCollateralUSD(
        terra,
        BLUNA_ADDRESS,
        ANCHOR_BLUNA_CUSTODY_ADDRESS
    )
    collateralBEthUSD = await getBTokenCollateralUSD(
        terra,
        BETH_ADDRESS,
        ANCHOR_BETH_CUSTODY_ADDRESS
    )

    totalCollateralUSD = collateralBLunaUSD + collateralBEthUSD

    print("-------------------------------------------")
    print("TVL", totalDepositUSD + totalCollateralUSD, "USD")
    print("totalDeposit", totalDepositUSD, "USD")
    print("totalCollateral", totalCollateralUSD, "USD")
    print("collateralBLuna", collateralBLunaUSD, "USD")
    print("collateralBEth", collateralBEthUSD, "USD")
    print("-------------------------------------------")

# uncomment to run the main() function
# asyncio.get_event_loop().run_until_complete(main())
