
import logging
from sqlalchemy import text

def create_filtered_results_table(engine):
    """
    Drops the existing `filtered_results` table if it exists, and recreates it with lowercase column names.
    """
    try:
        # Drop the table if it exists
        with engine.begin() as conn:  # Begin a transaction
            conn.execute(text("DROP TABLE IF EXISTS filtered_results;"))
            logging.info("Dropped the existing filtered_results table.")

        # Create the table with lowercase column names
        create_table_query = """
        CREATE TABLE filtered_results (
            id SERIAL PRIMARY KEY,
            seccode VARCHAR(10),
            companyname VARCHAR(255),
            fiscalyearend DATE,
            quarter VARCHAR(10),
            growth_percentage NUMERIC,
            projected_growth_rate NUMERIC,
            growth_percentage_opvalue NUMERIC,
            projected_growth_rate_opvalue NUMERIC,
            quarterenddate DATE,
            filingdate DATE,
            earn_flag VARCHAR(50),
            div_flag VARCHAR(50),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with engine.begin() as conn:  # Begin a new transaction
            conn.execute(text(create_table_query))
            logging.info("Created the filtered_results table with lowercase column names successfully.")
    except Exception as e:
        logging.error(f"Error creating or replacing the filtered_results table: {e}")
        raise

def insert_filtered_results(engine, filtered_data):
    """
    Inserts data into the `filtered_results` table.
    """
    insert_query = """
    INSERT INTO filtered_results (
        seccode, companyname, fiscalyearend, quarter, growth_percentage,
        projected_growth_rate, growth_percentage_opvalue, projected_growth_rate_opvalue,
        quarterenddate, filingdate, earn_flag, div_flag
    ) VALUES (
        :seccode, :companyname, :fiscalyearend, :quarter, :growth_percentage,
        :projected_growth_rate, :growth_percentage_opvalue, :projected_growth_rate_opvalue,
        :quarterenddate, :filingdate, :earn_flag, :div_flag
    );
    """
    try:
        with engine.begin() as conn:
            for _, row in filtered_data.iterrows():
                conn.execute(
                    text(insert_query),
                    {
                        'seccode': row.get('seccode', None),
                        'companyname': row.get('companyname', None),
                        'fiscalyearend': row.get('fiscalyearend', None),
                        'quarter': row.get('quarter', None),
                        'growth_percentage': row.get('growth_percentage', None),
                        'projected_growth_rate': row.get('projected_growth_rate', None),
                        'growth_percentage_opvalue': row.get('growth_percentage_opvalue', None),
                        'projected_growth_rate_opvalue': row.get('projected_growth_rate_opvalue', None),
                        'quarterenddate': row.get('quarterenddate', None),
                        'filingdate': row.get('filingdate', None),
                        'earn_flag': row.get('earn_flag', None),  # Use .get() to avoid KeyError
                        'div_flag': row.get('div_flag', None)     # Use .get() to avoid KeyError
                    }
                )
            logging.info("Data inserted and committed successfully into the filtered_results table.")
    except Exception as e:
        logging.error(f"Error inserting data into the filtered_results table: {e}")
        raise
