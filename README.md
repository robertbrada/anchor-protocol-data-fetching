# anchor-protocol-data-fetching
A single script that queries and computes the following data about Anchor Protocol from on-chain available data:
- Total Value Locked (USD)
- Total Deposit (USD)
- Total Collateral (USD)

There are two versions - Python and JavaScript. The Python version displays data in the browser in the Prometheus-compatible format, 

<br /> 

Anchor Protocol App: https://app.anchorprotocol.com/

Anchor Protocol Docs: https://docs.anchorprotocol.com/

Terra Finder: https://finder.terra.money/

Prometheus: https://prometheus.io/

# Run the script

## Python3 version

1. `1. git clone https://github.com/robertbrada/anchor-protocol-data-fetching.git`

2. `cd anchor-protocol-data-fetching/py`

3. (consider creating Python virtual environment for this project)

4. `pip3 install -r requirements.txt`

5. `python3 server.py`

6. Open browser window at http://127.0.0.1:8000/metrics

7. You should see the metrics in Prometheus-compatible format. The values will change when you refresh the window.

## JavaScript version

Note: JavaScript version does not show results in Prometheus format. In only print results to the terminal.

`git clone https://github.com/robertbrada/anchor-protocol-data-fetching.git`

`cd anchor-protocol-data-fetching/js`

`npm install`

`node index.js`