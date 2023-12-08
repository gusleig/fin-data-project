import os

import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

db_user = os.environ.get("DB_USERNAME")
db_pass = os.environ.get("DB_PASSWORD")
db_name = os.environ.get("DB_NAME")

connection_string = f"postgresql+psycopg2://{db_user}:{db_pass}@timescaledb:5432/{db_name}"

print(f"Connecting to database: {connection_string}")

# check if there is an database string in the .env file
if connection_string:
    db = connection_string
else:
    print("No database string specified in .env file. Please fix and run again.")
    sys.exit(1)

engine = create_engine(db)
engine.connect()

pprint(f"connection successful! : {engine}")

Session = sessionmaker(bind=engine)

Base = declarative_base()
