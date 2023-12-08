from flask import Flask, jsonify, request
from flask import render_template
from flask_bootstrap import Bootstrap
from datetime import datetime
import os
import psycopg2

os.system('ls')

FLASK_PORT = os.environ.get('FLASK_PORT')

print(f"RUNNING PORT: {FLASK_PORT}")

app = Flask(__name__, template_folder='templates')
Bootstrap(app)


def get_db_connection():
    conn = psycopg2.connect(host=os.environ.get("DB_HOST"),
                            database=os.environ.get("DB_NAME"),
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM crypto_hist_ht ORDER BY time desc LIMIT 10;')
    data = enumerate(cur.fetchall())
    date = datetime.now()
    cur.close()
    conn.close()
    return render_template('index.html', data=data, date=date)


@app.route('/daily/')
def daily():
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT
          time_bucket('1 day', time) AS bucket,
          ticker,
          first(close, time) AS open,
          max(high) AS high,
          min(low) AS low,
          last(close, time) AS close
        FROM 
            crypto_hist_ht srt
        WHERE 
            time > now() - INTERVAL '1 week'
        GROUP BY bucket, ticker
        ORDER BY bucket DESC
        LIMIT 10;
    
    """
    cur.execute(query)
    data = enumerate(cur.fetchall())
    cur.close()
    conn.close()
    date = datetime.now()
    return render_template('daily.html', data=data, date=date)


@app.route('/realtime/')
def realtime():
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT
            time, ticker, open_price , high_price , low_price , close_price, volume
        FROM 
            crypto_ht srt
        WHERE 
            time > now() - INTERVAL '1 week'
        ORDER BY time DESC
        LIMIT 10;

    """
    cur.execute(query)
    data = enumerate(cur.fetchall())
    cur.close()
    conn.close()
    date = datetime.now()
    return render_template('realtime.html', data=data, date=date)

@app.route('/about/')
def about():
    return render_template('about.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=FLASK_PORT)