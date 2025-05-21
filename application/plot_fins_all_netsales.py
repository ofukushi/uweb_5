

import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from sqlalchemy import create_engine
from dotenv import load_dotenv
import matplotlib
from matplotlib.dates import DateFormatter, YearLocator
from io import BytesIO
from datetime import datetime, timedelta
import numpy as np

matplotlib.use('Agg')

# Calculate the start and end dates based on the current date
end_date = datetime.now()
# start_date = end_date - timedelta(days=10*365)  # Approximately 10 years before
start_date = end_date - timedelta(days=5*365)  # Approximately 5 years before
end_date_plus_margin = end_date + timedelta(days=45)  # 45日分の余白を追加

def plot_qonq_growth(seccode, engine):
    # Query for NetSales QonQ growth data and projected growth rate
    netsales_query = """
    SELECT "fiscalyearend", "quarter", "quarterenddate", "growth_percentage", "projected_growth_rate", "companyname"
    FROM "u_fins_all_netsales"
    WHERE "seccode" = %s
    ORDER BY "quarterenddate"
    """
    netsales_df = pd.read_sql(netsales_query, engine, params=(seccode,))

    if netsales_df.empty:
        raise ValueError(f"No NetSales growth data found for sec code: {seccode}")

    # Ensure the dates are in datetime format
    netsales_df['quarterenddate'] = pd.to_datetime(netsales_df['quarterenddate'])

    # Replace None or NaN in 'CompanyName' with a default value
    netsales_df['companyname'] = netsales_df['companyname'].fillna('Unknown Company')

    # Convert growth_percentage and projected_growth_rate to numeric, forcing any errors to NaN
    netsales_df['growth_percentage'] = pd.to_numeric(netsales_df['growth_percentage'], errors='coerce')
    netsales_df['projected_growth_rate'] = pd.to_numeric(netsales_df['projected_growth_rate'], errors='coerce')

    # Filter out rows only if both growth_percentage and projected_growth_rate are NaN
    netsales_df = netsales_df.dropna(subset=['growth_percentage', 'projected_growth_rate'], how='all')

    # Sort by the quarter end date
    netsales_df.sort_values(by='quarterenddate', inplace=True)

    # Get the company name for the title
    companyname = netsales_df['companyname'].iloc[0]

    # Construct the full path to the font file
    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansJP[wght].ttf')
    font_prop = fm.FontProperties(fname=font_path)
    
    fig, ax1 = plt.subplots(figsize=(18, 4))

    # Plot NetSales QonQ growth percentage with green "x" markers as step plot
    if not netsales_df['growth_percentage'].isna().all():
        ax1.step(netsales_df['quarterenddate'], netsales_df['growth_percentage'], 
                 label='NetSales Growth (Q on Q)', color='orange', where='mid', marker='x', markerfacecolor='green', markeredgecolor='green')

    # Plot the entire projected growth rate as one line, using light blue "x" markers
    if not netsales_df['projected_growth_rate'].isna().all():
        ax1.step(netsales_df['quarterenddate'], netsales_df['projected_growth_rate'], 
                 label='Projected Growth Rate', color='blue', where='mid', linestyle='-', marker='x', markersize=4, markerfacecolor='lightblue', markeredgecolor='lightblue')

    # Initialize a flag to track whether the FY End label has been added to the legend
    label_added = False

   # Overlay large red stars specifically at FY end points
    for date, quarter, projected_rate in zip(netsales_df['quarterenddate'], netsales_df['quarter'], netsales_df['projected_growth_rate']):
        if quarter == "FY" and pd.notnull(projected_rate):
            if not label_added:
                ax1.scatter(date, projected_rate, color='red', marker='*', s=100, label='FY End')
                label_added = True  # Set the flag to True after adding the label
            else:
                ax1.scatter(date, projected_rate, color='red', marker='*', s=100)  # No label after the first point
            
            # Draw a vertical line at the fiscal year-end date
            ax1.axvline(date, color='black', linestyle=':', alpha=0.7)

    # Add the legend to the plot (only if at least one "FY End" marker was added)
    if label_added:
        ax1.legend()

    ax1.axhline(0, color='red', linestyle='--')

    ax1.set_xlabel('Date', fontproperties=font_prop)
    ax1.set_ylabel('Growth (%)', fontproperties=font_prop)
    ax1.set_title(f'Quarterly NetSales Growth (Q on Q) and Projected Growth Rate for {companyname} (Sec Code {seccode})', fontproperties=font_prop)

    ax1.yaxis.set_label_position("right")
    ax1.yaxis.tick_right()

    # Set the x-axis to the calculated start_date and end_date
    ax1.set_xlim(start_date, end_date_plus_margin)

    # X-axis formatting to show only the year
    ax1.xaxis.set_major_locator(YearLocator())  # Display major ticks at each year
    ax1.xaxis.set_major_formatter(DateFormatter('%Y'))  # Format the tick labels as year only
    plt.setp(ax1.get_xticklabels(), rotation=0, fontproperties=font_prop)

    # Add grid lines
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Add legend
    ax1.legend(loc='upper left', prop=font_prop)

    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', pad_inches=0.02)
    plt.close()
    img.seek(0)

    return img, companyname

# テスト実行用
if __name__ == "__main__":
    load_dotenv()
    database_url = os.getenv('LOCAL_DATABASE_URL').replace('postgres://', 'postgresql+psycopg2://')
    engine = create_engine(database_url)

    # 画像保存用のフォルダパスを設定
    output_folder = "output_images"
    # フォルダが存在しない場合は作成
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    img, companyname = plot_qonq_growth('1301', engine)
    # ファイルパスを指定
    file_path = os.path.join(output_folder, f'average_sales_growth_{companyname}.png')

    # ファイルを保存
    with open(file_path, 'wb') as f:
        f.write(img.getbuffer())

    print(f"Image saved to {file_path}")

# python plot_fins_yesterday_netsales.py