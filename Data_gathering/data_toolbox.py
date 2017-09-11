# API
import requests

# Basics
import numpy as np
import pandas as pd

# Time management
import datetime
import time

# Plotly
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.tools as tls

# Home made
from candle_stick_plot import generate_candle_stick


#
#   API requests limit: for tier 2, 15 requests available. 1 request is made available every 3 seconds, with max of 15
#   If limit reached: suspended for 15mn
#   Ledger/trade history: =2 requests
#
#

def api_call(url, params={}, datatype="json"):
    """
    Return API result

    :param url: str
    :param params: dict of key-value pair: {'name of param' : param_value }
    DEFAULT empty dict
    :param datatype: str, json/xml/raw: type of returned data
    DEFAULT json
    :return:
    """

    if datatype == 'json':
        return requests.get(
            url,
            params=params
        ).json()

    elif datatype == "xml":
        return requests.get(
            url,
            params=params).xml()

    elif datatype == "raw":
        return requests.get(
            url,
            params=params
        )


def json_to_pandas(input_data):
    """
    Return normalized dataframe from json
    :param input_data: json file, ex. from api_call with type='json'
    :return:
    """
    return pd.io.json.json_normalize(input_data)


def get_cur_time():
    """

    :return: datetime.datetime object
    """
    # TODO consider time zones
    # URL
    url_time = "https://api.kraken.com/0/public/Time"
    result = api_call(url_time)
    df = json_to_pandas(result)

    return datetime.datetime.fromtimestamp(
        int(df["result.unixtime"])
    ).strftime('%Y-%m-%d %H:%M:%S')


def get_asset_info(params={}):
    """
    Return complete Dataframe of getAssetInfo kraken API and list of assets, as a flatten array
    :param: params,dict ex:   params = {
                            "aclass": "currency",
                            "asset": "ZEUR"
                        }
    :return:
        <asset_name> = asset name
        altname = alternate name
        aclass = asset class
        decimals = scaling decimal places for record keeping
        display_decimals = scaling decimal places for output display
    """

    #
    #   Base currency or Transaction currency: first currency appearing in a currency pair quotation: PREFIX X
    #   Quote currency                       : second currency    "       "                           PREFIX Z
    #

    # URL
    url_asset = "https://api.kraken.com/0/public/Assets"

    # result
    df = api_call(url_asset, params=params)["result"]
    df = json_to_pandas(df)

    # Retrieve assets
    list_asset = set([asset.split(".")[1] for asset in df.columns.values if asset != "error"])
    print(list_asset)
    return df, list_asset


def get_tradable_asset_pair(params={}):
    """
    Return complete Dataframe of getAssetInfo kraken API and list of assets, flatten array
    :param: params,dict ex:   params = {
                            "info": "info"/"leverage"/"fees"/"margin",
                            "pair": ["ZEUR", "XETCXETH", ...]  # can be a list !
                        }
    :return:
        altname = alternate pair name
        aclass_base = asset class of base component
        base = asset id of base component
        aclass_quote = asset class of quote component
        quote = asset id of quote component
        lot = volume lot size
        pair_decimals = scaling decimal places for pair
        lot_decimals = scaling decimal places for volume
        lot_multiplier = amount to multiply lot volume by to get currency volume
        leverage_buy = array of leverage amounts available when buying
        leverage_sell = array of leverage amounts available when selling
        fees = fee schedule array in [volume, percent fee] tuples
        fees_maker = maker fee schedule array in [volume, percent fee] tuples (if on maker/taker)
        fee_volume_currency = volume discount currency
        margin_call = margin call level
        margin_stop = stop-out/liquidation margin level
    """
    # TODO understand formatting of pair

    #
    #   Base currency or Transaction currency: first currency appearing in a currency pair quotation: PREFIX X
    #   Quote currency                       : second currency    "       "                           PREFIX Z
    #

    # URL
    url_asset = "https://api.kraken.com/0/public/AssetPairs"

    # result
    df = api_call(url_asset, params=params)["result"]
    df = json_to_pandas(df)

    return df


def get_ticker_info(params={"pair": "XETHXEUR"}):
    """
    :param: params, dict. {"pair": "XETHXEUR"  # string only !
    :return:
        a = ask array(<price>, <whole lot volume>, <lot volume>),
        b = bid array(<price>, <whole lot volume>, <lot volume>),
        c = last trade closed array(<price>, <lot volume>),
        v = volume array(<today>, <last 24 hours>),
        p = volume weighted average price array(<today>, <last 24 hours>),
        t = number of trades array(<today>, <last 24 hours>),
        l = low array(<today>, <last 24 hours>),
        h = high array(<today>, <last 24 hours>),
        o = today's opening price
    """
    # URL
    url = "https://api.kraken.com/0/public/Ticker"

    # API Call
    df = api_call(url, params=params)["result"]
    df = json_to_pandas(df)

    return df


def get_ohlc(params={"pair": "XETHZEUR", "interval":1, }):
    """
    Return necessary data to plot a candle stick plot
    (see http://stockcharts.com/school/doku.php?id=chart_school:chart_analysis:introduction_to_candlesticks
     for a good explanation of this graph)
    :param: params, dict. ex: { "pair": "XETHXEUR"  # string only
    :return:
<pair_name> = pair name
    array of array entries(<time>, <open>, <high>, <low>, <close>, <vwap>, <volume>, <count>)
    last = id to be used as since when polling for new, committed OHLC data
    """
    # URL
    url = "https://api.kraken.com/0/public/OHLC"

    # API Call
    df = api_call(url, params=params)

    if df["error"]:
        raise ValueError(df["error"])

    df = json_to_pandas(df)

    # Numeric values
    df_value = df["result." + params["pair"]].iloc[0]
    df_value = [[float(j) for j in i] for i in df_value]

    # Last
    df_last = df["result.last"]

    # TODO precision enough ?
    val = np.asarray(df_value, dtype=np.float64)

    # Time converting
    val_index = [datetime.datetime.fromtimestamp(
        int(time)
    ).strftime('%Y-%m-%d %H:%M:%S')
                 for time in val[:, 0]
                 ]
    # Dataframe enclosing
    d = {
        "x": val_index,
         "Open": val[:, 1],
         "High": val[:, 2],
         "Low": val[:, 3],
         "Close": val[:, 4],
         "Volume": val[:, 6]
         }
    index = range(0, val.shape[0])
    df = pd.DataFrame(data=d, index=index)

    return df


if __name__ == "__main__":

    tls.set_credentials_file(username='LouisDge', api_key='GhcHOWrYTxpQr8fhFfWj', stream_ids=["0thkdchyt8",
                                                                                              "aitkv6svy2",
                                                                                              "jgk0jkcnel",
                                                                                              "h2vl4khzvy"])

    # Plotly identification
    stream_ids = tls.get_credentials_file()['stream_ids']
    print(stream_ids)
    
    # Get stream id from stream id list
    stream_id = stream_ids[0]

    # Make instance of stream id object
    stream_1 = go.Stream(
        token=stream_id,  # link stream id to 'token' key
        maxpoints=80  # keep a max of 80 pts on screen
    )

    # Retrieve Data
    df = get_ohlc()

    # generate graph
    generate_candle_stick(df, stream_id=stream_1, plot_name="Complete Price chart")

    # We will provide the stream link object the same token that's associated with the trace we wish to stream to
    s = py.Stream(stream_id)

    # TODO Streaming !! Adapt Range of data (day, week, month, etc.)
    # TODO Add title

    # We then open a connection
    s.open()

    start = time.time()
    time.sleep(5)

    while time.time() - start < 60:
        # Retrieve Data
        val, last = get_ohlc()

        # Time converting
        val_index = [datetime.datetime.fromtimestamp(
            int(time)
        ).strftime('%Y-%m-%d %H:%M:%S')
                     for time in val[:, 0]
                     ]

        # Write the new data
        s.write(dict(x=val_index,
                     open=val[:, 1],
                     high=val[:, 2],
                     low=val[:, 3],
                     close=val[:, 4],
                     ))

        time.sleep(15)

    s.close()





