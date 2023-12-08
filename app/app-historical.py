import matplotlib.pyplot as plt
import numpy as np
import os
import sqlalchemy
import pandas as pd
import ta.momentum
import ta.trend
import ta.volatility
from binance.client import Client
from sql import engine, Session
from sqlalchemy.sql import text

API_KEY = os.environ.get("BINANCE_API_KEY")
API_SECRET = os.environ.get("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET, tld='us')


def technicals(df, ema_slow1=200, ema_fast1=50, sma_slow2=25, sma_fast2=7):

    df['%K'] = ta.momentum.stoch(df.High, df.Low, df.Close, window=14, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df.Close, window=14)
    df['macd'] = ta.trend.macd_diff(df.Close)

    df['EMA200'] = ta.trend.ema_indicator(df.Close, window=ema_slow1)

    df['SMA50'] = ta.trend.sma_indicator(df.Close, window=20)
    df['SMA20'] = ta.trend.sma_indicator(df.Close, window=50)
    df['SMA100'] = ta.trend.sma_indicator(df.Close, window=100)

    df['EMA_slow1'] = ta.trend.ema_indicator(df.Close, window=ema_slow1)
    df['EMA_fast1'] = ta.trend.ema_indicator(df.Close, window=ema_fast1)

    df['SMA_fast2'] = ta.trend.sma_indicator(df.Close, window=sma_fast2)
    df['SMA_slow2'] = ta.trend.sma_indicator(df.Close, window=sma_slow2)

    df['Buy_sma2'] = 0.0
    df['Buy_sma2'] = np.where((df['SMA20'] > df['SMA50']) & (df['SMA50'] > df['SMA100']), 1.0, 0.0)

    df['position_sma'] = df['Buy_sma2'].diff()

    df['wf_Top_bool'] = np.where(df['High'] == df['High'].rolling(9, center=True).max(), True, False)

    df['wf_Top'] = np.where(df['High'] == df['High'].rolling(9, center=True).max(), df['High'], np.NaN)

    df['wf_Top'] = df['wf_Top'].ffill()

    df.dropna(inplace=True)

    # william's fractal indicator strategy

    df['Buy_fractal'] = np.where((df.Close > df.wf_Top) & (df.Close > df.EMA200), 1, 0)
    df['SL'] = np.where(df.Buy_fractal == 1, df.Close - (df.Close - df.Low), 0)
    df['TP'] = np.where(df.Buy_fractal == 1, df.Close + (df.Close - df.Low) * 1.5, 0)

    df.dropna(inplace=True)

    df.columns = map(str.lower, df.columns)
    df.columns = df.columns.str.replace('%', '')

    return df


def get_minute_data(symbol: str, lookback: int = 360) -> pd.DataFrame:
    print(f"Loading Binance data (5min candles) for {symbol}")
    frame = pd.DataFrame(client.get_historical_klines(symbol, '5m', str(lookback) + ' days ago UTC'))
    print("Loading OK")

    frame = frame.iloc[:, :5]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close']
    frame[['Open', 'High', 'Low', 'Close']] = frame[['Open', 'High', 'Low', 'Close']].astype(float)
    frame.Time = pd.to_datetime(frame.Time, unit='ms')

    return frame


def plot_chart(df):

    fig = plt.figure(figsize=(12, 10))

    price_ax = plt.subplot(2, 1, 1)

    price_ax.plot(df[['Close', 'SMA20', 'SMA50']])

    price_ax.plot(df[df.position_sma == 1].index, df['Close'][df['position_sma'] == 1], linestyle='None', marker='^',
                  markersize=15, color='g', label='buy')

    price_ax.legend(['Close', 'SMA20', 'SMA50', 'SMA100'], loc="upper left")

    roc_ax = plt.subplot(2, 1, 2, sharex=price_ax)

    roc_ax.plot(df[['rsi']], label="RSI", color="red")

    roc_ax.legend(loc="upper left")
    price_ax.set_title("BTC Prices and SMA/RSI indicators")

    # Removing the date labels and ticks from the price subplot:
    price_ax.get_xaxis().set_visible(False)

    # Removing the gap between the plots:
    fig.subplots_adjust(hspace=0)
    # Adding a horizontal line at the zero level in the ROC subplot:
    roc_ax.axhline(50, color=(.5, .5, .5), linestyle='--', alpha=0.5)
    roc_ax.axhline(20, color=(.5, .5, .5), linestyle='--', alpha=0.5)
    roc_ax.axhline(80, color=(.5, .5, .5), linestyle='--', alpha=0.5)

    # We can add labels to both vertical axis:
    price_ax.set_ylabel("Price ($)")
    roc_ax.set_ylabel("RSI")

    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                        hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())

    plt.show()


def get_binance_data(coins: list[str], db_engine: any, days: int = 10):

    session = Session()

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS crypto_hist_ht(
        time TIMESTAMPTZ NOT NULL,
        ticker varchar(20), 
        open float, 
        high float, 
        low float, 
        close float, 
        k float, 
        d float,
        rsi float,
        macd float,
        ema200 float,
        sma50 float,
        sma20 float,
        sma100 float,
        ema_slow1 float,
        ema_fast1 float,
        sma_fast2 float,
        sma_slow2 float,
        buy_sma2 float,
        position_sma float,
        wf_top_bool boolean,
        wf_top float,
        buy_fractal float,
        sl float,
        tp float
        );
    """

    session.execute(text(create_table_sql))
    try:
        session.execute(text("SELECT create_hypertable('crypto_hist_ht', 'time');"))
        session.commit()
    except sqlalchemy.exc.DatabaseError as err:
        print(err)

    for coin in coins:

        insert_select = f"""
            INSERT INTO crypto_hist_ht 
                (time, ticker, open, high, low, close, k, d, rsi, macd, ema200, sma50, sma20, sma100, ema_slow1, ema_fast1, sma_fast2, sma_slow2, buy_sma2, position_sma, wf_top_bool, wf_top, buy_fractal, sl, tp)
            select 
                Time, '{coin}', Open, High, Low, Close, k, d, rsi, macd, ema200, sma50, sma20, sma100, ema_slow1, ema_fast1, sma_fast2, sma_slow2, buy_sma2, position_sma, wf_top_bool, wf_top, buy_fractal, sl, tp
            from {coin};
        """

        print(f"Downloading {coin} from binance data looking back {days} days...")
        frame = get_minute_data(coin, days)

        # print("Performing technical analysis...")
        frame = technicals(frame)

        # plot_chart(frame)

        frame.to_sql(coin.lower(), db_engine, index=False, if_exists='replace')

        session = Session()
        session.execute(text(insert_select))
        session.commit()

        print(f"Created table {coin.lower()} and loaded it into crypto_hist_ht")


my_coins = ['BTCUSDT']
get_binance_data(my_coins, engine, 30)
