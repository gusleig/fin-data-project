#!/bin/bash

psql postgres <<-END
  -- Create a user and database for the application
  CREATE USER ${DB_USERNAME} WITH PASSWORD '${DB_PASSWORD}';

  CREATE DATABASE ${DB_NAME};

  GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} to ${DB_USERNAME};

  \c ${DB_NAME} ${DB_USERNAME};

  CREATE EXTENSION IF NOT EXISTS timescaledb;
  CREATE EXTENSION IF NOT EXISTS timescaledb_toolkit;

  -- Create app tables

  CREATE TABLE IF NOT EXISTS crypto_ht(
      ticker TEXT NOT NULL,
      close_price float,
      open_price float,
      high_price float,
      low_price float,
      volume float,
      time TIMESTAMPTZ NOT NULL
  );

  SELECT create_hypertable('crypto_ht', 'time');

  CREATE TABLE IF NOT EXISTS crypto_hist_ht(
      time TIMESTAMPTZ NOT NULL,
      ticker TEXT NOT NULL,
      open float,
      high float,
      low float,
      close float,
      k float,
      d float,
      rsi float,
      macd float,
      ema200 float,
      sma50 float,
      sma20 float,
      sma100 float,
      ema_slow1 float,
      ema_fast1 float,
      sma_fast2 float,
      sma_slow2 float,
      buy_sma2 float,
      position_sma float,
      wf_top_bool boolean,
      wf_top float,
      buy_fractal float,
      sl float,
      tp float
  );

  SELECT create_hypertable('crypto_hist_ht', 'time');
END
