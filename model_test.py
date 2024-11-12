import pandas as pd
import pymysql
import db_config
from sqlalchemy import create_engine

# conn = pymysql.connect(host=db_config.db_host, user=db_config.db_user, password=db_config.db_password, database=db_config.db_name, autocommit=
engine = create_engine(f'mysql+pymysql://{db_config.db_user}:{db_config.db_password}@{db_config.db_host}:{db_config.db_port}/{db_config.db_name}')

fetch_query = f"select * from `template_20240731`"
dataframe = pd.read_sql(sql=fetch_query, con=engine)

print(dataframe)
