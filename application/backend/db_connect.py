

import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

def get_database_engine():
    load_dotenv()
    
    # Detect environment
    #is_heroku = "DYNO" in os.environ    
    is_heroku = True
    database_url = os.getenv('HEROKU_DATABASE_URL') if is_heroku else os.getenv('LOCAL_DATABASE_URL')
    database_url = database_url.replace('postgres://', 'postgresql+psycopg2://')

    # Create engine with connection pooling
    engine = create_engine(
        database_url,
        pool_size=10,           # Base pool size
        max_overflow=5,          # Max extra connections if pool is full
        pool_timeout=30,         # Timeout to get connection
        pool_recycle=1800        # Recycle connections every 30 minutes
    )
    return engine
