# Findata 

## Setup Binance API keys 

Create a .env file in the root of the project and add the following variables

```
  BINANCE_API_KEY=my-api-key
  BINANCE_API_SECRET=my-api-secret
  DB_USERNAME=findata
  DB_PASSWORD=Findata1234
  DB_NAME=findatadb
```

## Docker setup

`docker-compose up --build`

# Manual install
## MacOS Postgresql install

`brew install postgresql@15`

Install psql

```
brew install libpq
brew link --force libpq
```

Export variables

```
echo 'export PATH="/usr/local/opt/libpq/bin:$PATH"' >> ~/.zshrc
export LDFLAGS="-L/usr/local/opt/libpq/lib"
export CPPFLAGS="-I/usr/local/opt/libpq/include"
export PKG_CONFIG_PATH="/usr/local/opt/libpq/lib/pkgconfig"

echo 'export PATH="/usr/local/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
export LDFLAGS="-L/usr/local/opt/postgresql@15/lib"
export CPPFLAGS="-I/usr/local/opt/postgresql@15/include"
export PKG_CONFIG_PATH="/usr/local/opt/postgresql@15/lib/pkgconfig"
```

## Start Postgresql

`brew services start postgresql@15`

Install timescaledb

```
brew tap timescale/tap
brew install timescaledb
```
Check your postgresql version (show data directory so you know where we are)

```
psql postgres
sql (16.1, server 15.5 (Homebrew))
Type "help" for help.

postgres=# SHOW data_directory;
        data_directory
------------------------------
 /usr/local/var/postgresql@15
(1 row)

```
Now use that path to create the timescaledb extension
```

timescaledb-tune --yes --conf-path="/usr/local/var/postgresql@15/postgresql.conf"

```

Run DB init script

```
CREATE USER findata WITH PASSWORD 'Findata1234';
CREATE DATABASE findatadb;
GRANT ALL PRIVILEGES ON DATABASE findatadb to findata;
\c "host=localhost  dbname=findatadb user=findata password=Findata1234";
CREATE EXTENSION IF NOT EXISTS timescaledb;
```