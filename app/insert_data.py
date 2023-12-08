from sql import engine, Base, Session
from sqlalchemy.sql import text


def create_table():
    # create a new session
    session = Session()
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS crypto_ht(
        ticker varchar(20), 
        close_price float, 
        open_price float, 
        high_price float, 
        low_price float, 
        volume float, 
        time TIMESTAMPTZ NOT NULL
        );
    """
    try:
        # Generate schema
        if not engine.dialect.has_table(engine.connect(), "crypto_ht"):
            # Base.metadata.create_all(engine)
            # session.commit()
            print(f"Main table created, adding hypertable")
            session.execute(text(create_table_sql))
            session.execute(text("SELECT create_hypertable('crypto_ht', 'time');"))
            session.commit()

    except Exception as e:
        session.rollback()
        print(e)

    session.close()
