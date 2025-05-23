
import os
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import mplfinance as mpf
from datetime import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv
from io import BytesIO
import matplotlib.font_manager as fm
from datetime import timedelta
import numpy as np

# Calculate the start and end dates based on the current date
end_date = datetime.now()
# start_date = end_date - timedelta(days=10*365)  # Approximately 10 years before
start_date = end_date - timedelta(days=5*365)  # Approximately 5 years before
# チャートの右端を見やすくするために新たに右端に余白を加えるためのend_date_plus_marginを計算 
end_date_plus_margin = end_date + timedelta(days=45)  # 45日分の余白を追加

def plot_combined_chart(seccode, engine):

    # Construct the full path to the font file
    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansJP[wght].ttf')
    print(f"Font path: {font_path}")  # Debugging font path
    font_prop = fm.FontProperties(fname=font_path)
    print(f"Font name: {font_prop.get_name()}")  # Debugging font name

    query = f'SELECT * FROM "u_fins_all_bps_opvalues" WHERE "seccode" = \'{seccode}\' ORDER BY "quarterenddate" ASC'

    df = pd.read_sql(query, engine)

    if df.empty:
        raise ValueError(f"No data found for Sec Code: {seccode}")

    df['quarterenddate'] = pd.to_datetime(df['quarterenddate'])
    df.sort_values(by='quarterenddate', inplace=True)
    companyname = df.iloc[-1]['companyname']

    fig, ax1 = plt.subplots(figsize=(18, 8))

    # Ensure that BPS and Operation Value stop at 0 even when negative
    bps_clipped = np.clip(df['bps'], 0, None)  # Clip the BPS values at 0
    bps_eval_clipped = np.clip(df['bps_eval'], 0, None)  # Clip the bps_eval values at 0
    opvalue_clipped = np.clip(df['bps_eval'] + df['opvalue'], 0, None)  # Clip the Operation Value at 0
    nextyrfcastfairvalue_clipped = np.clip(df['nextyrfcastfairvalue'], 0, None) # Clip forecasted fair value at 0

    # Fill between 0 and bps, and between bps and opvalue, stopping at 0 for negative values
    ax1.fill_between(df['quarterenddate'], 0, bps_eval_clipped, color='lightblue', alpha=0.3, step='mid', label='BPS')
    ax1.fill_between(df['quarterenddate'], bps_eval_clipped, opvalue_clipped, color='lightcoral', alpha=0.3, step='mid', label='Operation Value')
    # Fill area between bps_eval_clipped and bps_clipped
    ax1.fill_between(df['quarterenddate'], bps_eval_clipped, bps_clipped, color='lightcyan', alpha=0.4, step='mid', label='BPS Fill Area')

    # Prioritize the blue line (bps_eval Line) with the highest z-order
    ax1.step(df['quarterenddate'], bps_eval_clipped, color='blue', label='bps_eval Line', linestyle='--', where='mid', zorder=3)
    ax1.step(df['quarterenddate'], opvalue_clipped, color='orange', label='Fair Value Line', linestyle='-', where='mid', zorder=1)
    ax1.step(df['quarterenddate'], nextyrfcastfairvalue_clipped, label='Fair Value', color='gray', marker='x', where='mid', zorder=2)
    # New: Add bps_clipped line (highlight with distinct color and style)
    ax1.step(df['quarterenddate'], bps_clipped, label='BPS Clipped Line', color='cyan', linestyle='-.', where='mid', zorder=4)

    q4_data = df[df['quarter'] == 'FY']
    ax1.scatter(q4_data['quarterenddate'], q4_data['bps_eval'], color='blue', label='bps_eval (FY)', marker='*', s=100)
    ax1.scatter(q4_data['quarterenddate'], q4_data['bps_eval'] + q4_data['nextyrfcastopvalue'], color='red', label='Next Operation Value (FY)', marker='*', s=100)
    ax1.scatter(q4_data['quarterenddate'], q4_data['fairvalue'], color='green', label='Fair Value (FY)', marker='*', s=100)
    # 🔥 New: Add Scatter plot for key `bps_clipped` points
    ax1.scatter(df['quarterenddate'], bps_clipped, label='BPS Clipped (Points)', color='cyan', marker='*', s=40, zorder=5)

    # 配当率ラインの追加
    df['adjusted_divannual_for_chart'] = df['adjusted_divannual_for_chart'].fillna(0)
    dividend_yield_line = df['adjusted_divannual_for_chart'] / 0.04
    if not dividend_yield_line.empty:
        ax1.step(df['quarterenddate'], dividend_yield_line, label='Dividend Yield (4%)', color='purple', linestyle='-', where='mid')

    # 追加: FcastDivAnnual_for_chartの配当ラインをプロット
    df['adjusted_fcastdivannual_for_chart'] = df['adjusted_fcastdivannual_for_chart'].fillna(0)
    fcast_dividend_yield_line = df['adjusted_fcastdivannual_for_chart'] / 0.04
    if not fcast_dividend_yield_line.empty:
        ax1.step(df['quarterenddate'], fcast_dividend_yield_line, label='Forecast Dividend Yield (4%)', color='red', linestyle='--', where='mid')

    ax1.set_xlabel('Disclosed Date', fontproperties=font_prop)
    ax1.set_ylabel('Value', fontproperties=font_prop)
    ax1.set_title(f'Fair Values for Company {seccode} - {companyname}', fontproperties=font_prop)
    # ax1.grid(True)
    ax1.grid(True, axis='y')  # ✅ show horizontal price lines only
    ax1.legend(loc='upper left', prop=font_prop)

    ax1.yaxis.set_label_position("right")
    ax1.yaxis.tick_right()

    import logging

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Attempt to download stock data
        logger.info(f"Attempting to download stock data for {seccode}.")
        # stock_data = yf.download(f"{seccode}.T", start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        stock_data = yf.download(
            f"{seccode}.T", 
            start=start_date.strftime('%Y-%m-%d'), 
            end=end_date.strftime('%Y-%m-%d'),
            auto_adjust=False,
            actions=True
        )

        # Check for multi-level columns and flatten if necessary
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = [col[0] for col in stock_data.columns]  # Flatten to single-level columns
            logger.info(f"Flattened stock data columns for {seccode}: {stock_data.columns.tolist()}")

        # Log the downloaded data's info to check completeness
        logger.info(f"Downloaded stock data columns for {seccode}: {stock_data.columns.tolist()}")
        
        # Required columns for processing
        required_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        
        # Check if stock_data contains the required columns, log and handle if not
        if stock_data.empty:
            raise ValueError(f"No data returned for stock {seccode}. Check if ticker is valid or data exists.")
        elif not set(required_columns).issubset(stock_data.columns):
            missing_columns = set(required_columns) - set(stock_data.columns)
            raise ValueError(f"Missing columns in stock data for {seccode}: {missing_columns}. This may be a yfinance issue.")

        # Resample monthly data if columns are present
        stock_data = stock_data.resample('W-FRI').agg({  #Use 'ME' for end of month, 'W-FRI' for end of week
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Adj Close': 'last',
            'Volume': 'sum'
        }).dropna()
        
        logger.info(f"Successfully processed stock data for {seccode}.")

    except Exception as e:
        logger.error(f"Failed to download or process stock data for {seccode} due to: {e}")
        img = BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', pad_inches=0.02)
        plt.close()
        img.seek(0)
        return img, companyname

    # mpf.plot(stock_data, type='candle', ax=ax1, style='charles', show_nontrading=True)
    mpf.plot(
        stock_data,
        type='ohlc',
        ax=ax1,
        style='charles',
        show_nontrading=True,
        update_width_config=dict(
            # candle_linewidth=0.5,
            # candle_width=5.0
            ohlc_linewidth=1.5,  # Make OHLC bars thicker
            ohlc_ticksize=3.0    # Extend open/close "ticks" wider
        )
    )

    #combined_dates = pd.date_range(start=min(df['quarterenddate'].min(), stock_data.index.min()), end=max(df['quarterenddate'].max(), stock_data.index.max()), freq='YS')
    # Use the same start_date and end_date for the x-axis limits
    ax1.set_xlim(start_date, end_date_plus_margin)

    # combined_dates = pd.date_range(start=start_date, end=end_date_plus_margin, freq='YS')   
    # combined_dates = pd.date_range(start=start_date, end=end_date_plus_margin, freq='6MS')  # Every 6 months
    combined_dates = pd.date_range(start=start_date, end=end_date_plus_margin, freq='2QS-JAN')

    for date in combined_dates:
        if date.month == 1:
            ax1.axvline(
                x=date,
                color='gray',
                linewidth=1.2,
                linestyle='-',   # solid line for January
                zorder=0
            )
        else:
            ax1.axvline(
                x=date,
                color='gray',
                linewidth=0.8,
                linestyle=(0, (4, 6)),  # dashed for July
                zorder=0
            )

    # Set the ticks (6-month grid lines: Jan + Jul)
    ax1.set_xticks(combined_dates)

    # Generate only the January label positions and text
    label_positions = [d for d in combined_dates if d.month == 1]
    label_texts = [d.strftime('%Y') for d in label_positions]

    # Set only the labeled ticks (once), with clean horizontal text
    ax1.set_xticks(label_positions)
    ax1.set_xticklabels(label_texts, fontproperties=font_prop, rotation=0)

    # 1. Calculate ymax
    ymax = max(
        df['bps'].max(),
        df['bps_eval'].max(),
        (df['bps_eval'] + df['opvalue']).max(),
        df['nextyrfcastfairvalue'].max(),
        df['adjusted_divannual_for_chart'].max() / 0.04,
        df['adjusted_fcastdivannual_for_chart'].max() / 0.04,
        df['fairvalue'].max(),
        stock_data['High'].max()
    )

    # 2. Set axis limits
    ax1.set_ylim(bottom=0, top=ymax * 1.1)

    # 3. Identify clipped series and collect names
    clipped_series = []
    if (df['bps'] < 0).any():
        clipped_series.append("bps")
    if (df['bps_eval'] < 0).any():
        clipped_series.append("bps_eval")
    if ((df['bps_eval'] + df['opvalue']) < 0).any():
        clipped_series.append("bps_eval + opvalue")
    if (df['nextyrfcastfairvalue'] < 0).any():
        clipped_series.append("nextyrfcastfairvalue")
    if (df['fairvalue'] < 0).any():
        clipped_series.append("fairvalue")
    if ((df['adjusted_divannual_for_chart'] / 0.04) < 0).any():
        clipped_series.append("dividend_yield")
    if ((df['adjusted_fcastdivannual_for_chart'] / 0.04) < 0).any():
        clipped_series.append("forecast_dividend_yield")

    # 4. Annotate if any value was clipped below zero
    if clipped_series:
        ax1.text(
            df['quarterenddate'].iloc[-1],
            ymax * 1.05,
            f"⚠️ CLIPPED: {', '.join(clipped_series)}",
            fontsize=12,
            color='red',
            ha='right',
            va='bottom'
        )

    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', pad_inches=0.02)
    plt.close()
    img.seek(0)

    return img, companyname

# テスト実行用
if __name__ == "__main__":

    load_dotenv()

    # Heroku環境かどうかを確認する
    heroku_env = os.getenv("HEROKU_ENV", "false").lower() == "true"
    if heroku_env:
        heroku_database_url = os.getenv('HEROKU_DATABASE_URL')
        heroku_database_url = heroku_database_url.replace('postgres://', 'postgresql+psycopg2://')
        engine = create_engine(heroku_database_url)
        print("Running in Heroku environment. Using Heroku database.")
    else:
        local_database_url = os.getenv('LOCAL_DATABASE_URL')
        local_database_url = local_database_url.replace('postgres://', 'postgresql+psycopg2://')
        engine = create_engine(local_database_url)
        print("Running in local environment. Using local database.")

    sec_code = "1515"  # テストするセキュリティコードを入力してください

    try:
        img, company_name = plot_combined_chart(sec_code, engine)
        plt.imshow(plt.imread(img))
        plt.axis('off')
        plt.show()
    except Exception as e:
        print(f"Failed to generate plot for Sec Code: {sec_code} due to {e}")

# python plot_fins_all_bps_opvalues.py