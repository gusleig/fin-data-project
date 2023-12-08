# Findata 

The data is collected from Binance API, we used historical data (last 30 days of 5min candles) and stored in a Postgresql database in a table called crypto_hist_ht indexed with Timescaledb .

I also used websocket to get data from Binance in realtime (1 min candles) and stored in a table called crypto_ht.

With the data stored in Postgresql, we could use advanced queries with timescaledb unique features,

After running the docker container, the Flask dashboard can be accessed at http://127.0.0.1:5029/

## Setup Binance API keys 

Create a .env file in the root of the project and add the following variables

```
  BINANCE_API_KEY=my-api-key
  BINANCE_API_SECRET=my-api-secret
  DB_USERNAME=findata
  DB_PASSWORD=Findata1234
  DB_NAME=findatadb
```

## Docker start

Please make sure you have docker desktop installed and running

`docker-compose up --build -d` 

Open your browser and go to http://127.0.0.1:5029/