import { LCDClient } from "@terra-money/terra.js";

// Contract addresses (https://docs.anchorprotocol.com/smart-contracts/deployed-contracts)
const ANCHOR_MARKET_ADDRESS = "terra1sepfj7s0aeg5967uxnfk4thzlerrsktkpelm5s";
const ANCHOR_ORACLE_ADDRESS = "terra1cgg6yef7qcdm070qftghfulaxmllgmvk77nc7t";
const ANCHOR_BLUNA_CUSTODY_ADDRESS =
  "terra1ptjp2vfjrwh0j0faj9r6katm640kgjxnwwq9kn";
const ANCHOR_BETH_CUSTODY_ADDRESS =
  "terra10cxuzggyvvv44magvrh3thpdnk9cmlgk93gmx2";
const BLUNA_ADDRESS = "terra1kc87mu460fwkqte29rquh4hc20m54fxwtsx7gp";
const BETH_ADDRESS = "terra1dzhzukyezv0etz22ud940z7adyv7xgcjkahuun";

// Connect to columbus network
const terra = new LCDClient({
  URL: "https://lcd.terra.dev",
  chainID: "columbus-5",
});

/**
 * Function that computes total deposit in Anchor Protocol
 * @returns {Number}
 */
async function getTotalDeposit() {
  // query data about Anchors's Market-Contract current state
  const response = await terra.wasm.contractQuery(ANCHOR_MARKET_ADDRESS, {
    state: {},
  });

  const aterra_supply = parseFloat(response["prev_aterra_supply"]); // aUST token Total Supply
  const exchange_rate = parseFloat(response["prev_exchange_rate"]);

  // divide by 10**6 in order to get the right USD value
  // aUST has 6 decimals: https://finder.terra.money/columbus-4/address/terra1hzh9vpxhsk8253se0vv5jj6etdvxu3nv8z07zu
  return (aterra_supply / 10 ** 6) * exchange_rate;
}

/**
 *  Function that computes total collateral value for a given bToken (on 28.1.2022 can be either bLUNA or bETH)
 * @param {string} bTokenAddress Address of bToken smart contract address
 * @param {string} bTokenAnchorCustodyAddress Address of Anchor's custody smart contract related to given bToken
 * @returns {Number} Total bToken Collateral
 */
async function getBTokenCollateral(bTokenAddress, bTokenAnchorCustodyAddress) {
  // Query bToken contract how much of it is bTokenAnchorCustody contract holding
  const balanceResponse = await terra.wasm.contractQuery(bTokenAddress, {
    balance: { address: bTokenAnchorCustodyAddress },
  });
  const bTokenBalance = parseFloat(balanceResponse.balance);

  // get price usd price of given bToken
  const priceResponse = await terra.wasm.contractQuery(ANCHOR_ORACLE_ADDRESS, {
    price: {
      base: bTokenAddress,
      quote: "uusd",
    },
  });
  const bTokenPrice = parseFloat(priceResponse.rate);

  // get token decimals (in order to compute corresponding USD value properly)
  const tokenInfoResponse = await terra.wasm.contractQuery(bTokenAddress, {
    token_info: {},
  });
  const tokenDecimals = tokenInfoResponse["decimals"];

  // return total collateral for the given bToken
  return bTokenPrice * (bTokenBalance / 10 ** tokenDecimals);
}

async function main() {
  const totalDeposit = await getTotalDeposit();
  const collateralBLuna = await getBTokenCollateral(
    BLUNA_ADDRESS,
    ANCHOR_BLUNA_CUSTODY_ADDRESS
  );
  const collateralBEth = await getBTokenCollateral(
    BETH_ADDRESS,
    ANCHOR_BETH_CUSTODY_ADDRESS
  );

  const totalCollateral = collateralBLuna + collateralBEth;

  console.log("-------------------------------------------");
  console.log(`Total Value Locked: ${totalDeposit + totalCollateral} USD`);
  console.log(`Total Deposit: ${totalDeposit} USD`);
  console.log(`Total Collateral: ${totalCollateral} USD\n`);
  console.log(`Collateral bLUNA: ${collateralBLuna} USD`);
  console.log(`Collateral bETH: ${collateralBEth} USD`);
  console.log("-------------------------------------------");
}

main();
