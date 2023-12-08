from sqlalchemy.sql import func
from sqlalchemy import Date, Column, Integer, String, Float, DateTime
from sql import Base


class CryptoPrice(Base):
    __tablename__ = "crypto_ht"
    # __table_args__ = {'schema': 'findata'}

    # id = Column(Integer, primary_key=True)
    ticker = Column(String(20))
    close_price = Column(Float())
    open_price = Column(Float())
    high_price = Column(Float())
    low_price = Column(Float())
    volume = Column(Float())
    time = Column(DateTime(timezone=True), server_default=func.now(), primary_key=True)

    def __int__(self, ticker, close_price, open_price, high_price, low_price, volume, time):
        self.ticker = ticker
        self.open_price = open_price
        self.close_price = close_price
        self.high_price = high_price
        self.low_price = low_price
        self.volume = volume
        self.time = time
