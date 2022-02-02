# anchor-protocol-data-fetching
A single script that queries and computes the following data about Anchor Protocol from on-chain available data:
- Total Value Locked (USD)
- Total Deposit (USD)
- Total Collateral (USD)

There are two versions - Python and JavaScript. 
- **Python version** displays data in the browser in the Prometheus-compatible format.
- **JavaScript version** only prints data to the console.

<br /> 

## Resources

Anchor Protocol App: https://app.anchorprotocol.com/

Anchor Protocol Docs: https://docs.anchorprotocol.com/

Terra Finder: https://finder.terra.money/

Prometheus: https://prometheus.io/

<br /> 

# Run the script

## Python3 version

1. `git clone https://github.com/robertbrada/anchor-protocol-data-fetching.git`

2. `cd anchor-protocol-data-fetching/py`

3. (consider creating [Python virtual environment](https://docs.python.org/3/tutorial/venv.html)  for this project)

4. `pip3 install -r requirements.txt`

5. `python3 server.py`

6. Open browser window at http://127.0.0.1:8000/metrics

7. You should see the metrics in Prometheus-compatible format. The values will change when you refresh the window. You should see something like this:

```
# HELP total_collateral_usd USD value of all collaterals
# TYPE total_collateral_usd gauge
total_collateral_usd 3210271598.154153
# HELP total_deposit_usd USD value of all deposits
# TYPE total_deposit_usd gauge
total_deposit_usd 5223343722.043455
# HELP tvl_usd Total USD value locked (collateral + deposit)
# TYPE tvl_usd gauge
tvl_usd 8433615320.197608
```

## JavaScript version

**Note:** JavaScript version does not show results in Prometheus format. In only print results to the terminal.

1. `git clone https://github.com/robertbrada/anchor-protocol-data-fetching.git`

2. `cd anchor-protocol-data-fetching/js`

3. `npm install`

4. `node index.js`