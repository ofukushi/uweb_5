
from application.backend.stock_price import get_latest_stock_price
import logging
import pandas as pd

def fetch_filtered_companies(engine, growth_percentage_threshold, projected_growth_rate_threshold, 
                             growth_percentage_opvalue_threshold, projected_growth_rate_opvalue_threshold, 
                             start_date, data_years, fairvalue_filter, filingdate):
    logging.info("Executing query on the following database: %s", engine.url)

    years_filter_condition = f"""
    HAVING EXTRACT(YEAR FROM MAX("quarterenddate"::DATE)) - EXTRACT(YEAR FROM MIN("quarterenddate"::DATE)) >= {data_years}
    """ if data_years is not None else ""

    base_condition_parts = []
    if growth_percentage_threshold != 'N/A':
        base_condition_parts.append(f'"growth_percentage" >= {growth_percentage_threshold} AND "growth_percentage" IS NOT NULL')
    if projected_growth_rate_threshold != 'N/A':
        base_condition_parts.append(f'"projected_growth_rate" >= {projected_growth_rate_threshold} AND "projected_growth_rate" IS NOT NULL')
    if growth_percentage_opvalue_threshold != 'N/A':
        base_condition_parts.append(f'"growth_percentage_opvalue" >= {growth_percentage_opvalue_threshold} AND "growth_percentage_opvalue" IS NOT NULL')
    if projected_growth_rate_opvalue_threshold != 'N/A':
        base_condition_parts.append(f'"projected_growth_rate_opvalue" >= {projected_growth_rate_opvalue_threshold} AND "projected_growth_rate_opvalue" IS NOT NULL')
    if filingdate:
        base_condition_parts.append(f'n."filingdate" >= \'{filingdate}\'::date')

    base_condition = " AND ".join(base_condition_parts)

    query = f"""
        WITH filtered_seccode AS (
            SELECT 
                "seccode",
                EXTRACT(YEAR FROM MAX("quarterenddate"::DATE)) - EXTRACT(YEAR FROM MIN("quarterenddate"::DATE)) AS years_diff
            FROM
                "u_fins_all_netsales"
            WHERE
                "companyname" != 'Unknown'
            GROUP BY "seccode"
            {years_filter_condition}
        )
        , latest_records AS (
            SELECT 
                n."seccode",
                n."companyname",
                n."fiscalyearend",
                n."growth_percentage",
                n."projected_growth_rate",
                b."growth_percentage_opvalue",
                b."projected_growth_rate_opvalue",
                b."fcastfairvalue",
                b."nextyrfcastfairvalue",
                n."quarterenddate",
                n."quarter",
                n."filingdate",
                n."earn_flag",  -- Use double quotes here
                n."div_flag",   -- Use double quotes here
                ROW_NUMBER() OVER (PARTITION BY n."seccode" ORDER BY n."quarterenddate" DESC, n."filingdate" DESC) AS rn
            FROM 
                "u_fins_all_netsales" n
            JOIN 
                filtered_seccode f ON n."seccode" = f."seccode"
            LEFT JOIN
                "u_fins_all_bps_opvalues" b
            ON
                n."seccode" = b."seccode" AND n."quarterenddate" = b."quarterenddate"
            WHERE 
                n."companyname" != 'Unknown'
                {f"AND n.filingdate = '{filingdate}'::date" if filingdate else ""}
            GROUP BY 
                n."seccode", n."companyname", n."fiscalyearend", n."growth_percentage", n."projected_growth_rate", 
                b."growth_percentage_opvalue", b."projected_growth_rate_opvalue", b."fcastfairvalue", b."nextyrfcastfairvalue", 
                n."quarterenddate", n."quarter", n."filingdate", n."earn_flag", n."div_flag"
        )
        SELECT * FROM latest_records 
        WHERE rn = 1
        AND "quarterenddate"::date >= '{start_date}'::date
        ORDER BY "seccode", "quarterenddate" DESC;
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            df[['growth_percentage', 'projected_growth_rate', 'growth_percentage_opvalue', 'projected_growth_rate_opvalue']] = df[
                ['growth_percentage', 'projected_growth_rate', 'growth_percentage_opvalue', 'projected_growth_rate_opvalue']
            ].round(2)

            if fairvalue_filter:
                filtered_rows = []
                for _, row in df.iterrows():
                    latest_stock_price = get_latest_stock_price(row['seccode'])
                    if latest_stock_price is None:
                        continue
                    if row['quarter'] == 'FY' and row['nextyrfcastfairvalue'] > latest_stock_price:
                        filtered_rows.append(row)
                    elif row['fcastfairvalue'] > latest_stock_price:
                        filtered_rows.append(row)
                df = pd.DataFrame(filtered_rows)
            total_companies = pd.read_sql('SELECT COUNT(DISTINCT "seccode") FROM fins_all_netsales WHERE "companyname" != \'Unknown\'', conn).iloc[0, 0]
            filtered_companies_count = df['seccode'].nunique()
    except Exception as e:
        logging.error(f"Error executing query: {e}")
        df = pd.DataFrame()
        total_companies = 0
        filtered_companies_count = 0

    return df, filtered_companies_count, total_companies
