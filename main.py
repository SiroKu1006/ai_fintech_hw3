# A1115530 
import yfinance as yf
import os
import pandas as pd
import matplotlib.pyplot as plt

tickers = ["AAPL", "TSLA", "BTC-USD"]
start_date = "2015-03-29"
end_date = "2025-03-29"

if not os.listdir("data"):
    for ticker in tickers:
        data = yf.download(ticker, start=start_date, end=end_date)
        filename = f"data/{ticker}.csv"
        data.to_csv(filename)
        print(f"儲存到：{filename}")

def load_stock_data(filepath):
    df = pd.read_csv(filepath, skiprows=3, header=None)
    df.columns = ["Date", "Close", "High", "Low", "Open", "Volume"]
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    return df




def apply_sma_strategy(df, short_window=10, long_window=50):
    df = df.copy()
    df["SMA_short"] = df["Close"].rolling(window=short_window).mean()
    df["SMA_long"] = df["Close"].rolling(window=long_window).mean()
    df["Signal"] = 0
    df["Signal"][df["SMA_short"] > df["SMA_long"]] = 1
    df["Position"] = df["Signal"].diff()
    return df.dropna()

def backtest(df, initial_capital=10000, trade_size=10):
    df = df.copy()
    cash = initial_capital
    shares = 0
    portfolio_values = []

    for date, row in df.iterrows():
        price = row["Close"]
        signal = row["Position"]

        # Buy
        if signal == 1:
            cost = trade_size * price
            if cash >= cost:
                cash -= cost
                shares += trade_size

        # Sell
        elif signal == -1 and shares >= trade_size:
            cash += trade_size * price
            shares -= trade_size

        # 記錄
        total_value = cash + shares * price
        portfolio_values.append((date, total_value))

    result_df = pd.DataFrame(portfolio_values, columns=["Date", "Portfolio Value"]).set_index("Date")
    return result_df

def plot_signals(df, ticker):
    plt.figure(figsize=(14,6))
    plt.plot(df.index, df["Close"], label="Price", alpha=0.6)
    plt.plot(df.index, df["SMA_short"], label="SMA short")
    plt.plot(df.index, df["SMA_long"], label="SMA long")

    plt.scatter(df[df["Position"] == 1].index, df[df["Position"] == 1]["Close"], label="Buy", marker="^", color="green")
    plt.scatter(df[df["Position"] == -1].index, df[df["Position"] == -1]["Close"], label="Sell", marker="v", color="red")

    plt.title(f"{ticker} - SMA Crossover Signals")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(f"data/{ticker}_signals.png")
    plt.close()

def plot_portfolio(portfolio_df, ticker):
    plt.figure(figsize=(10,4))
    plt.plot(portfolio_df, label="Portfolio Value")
    plt.title(f"{ticker} - Backtest Portfolio Value")
    plt.xlabel("Date")
    plt.ylabel("Value ($)")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(f"data/{ticker}_portfolio.png")
    plt.close()

def main():
    tickers = ["AAPL", "TSLA", "BTC-USD"]
    for ticker in tickers:
        filepath = f"data/{ticker}.csv"
        if not os.path.exists(filepath):
            print(f"找不到 {filepath}")
            continue

        print(f"\n處理中：{ticker}")
        df = load_stock_data(filepath)
        df_sma = apply_sma_strategy(df)


        portfolio_df = backtest(df_sma)

        plot_signals(df_sma, ticker)
        plot_portfolio(portfolio_df, ticker)

        total_return = (portfolio_df["Portfolio Value"].iloc[-1] - portfolio_df["Portfolio Value"].iloc[0]) / portfolio_df["Portfolio Value"].iloc[0] * 100
        max_drawdown = (portfolio_df["Portfolio Value"].cummax() - portfolio_df["Portfolio Value"]).max()
        print(f"{ticker} 總報酬率：{total_return:.2f}%")
        print(f"最大回落：${max_drawdown:.2f}")

if __name__ == "__main__":
    main()