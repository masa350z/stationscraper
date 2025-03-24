import os
import psycopg2
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# DB接続情報（docker-composeの環境変数）
DB_HOST = os.environ.get("DB_HOST", "db")
DB_USER = os.environ.get("POSTGRES_USER", "stationuser")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "stationpass")
DB_NAME = os.environ.get("POSTGRES_DB", "stationdb")

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )


@app.route("/")
def index():
    # ルートURLへのアクセス時に、static/index.htmlを返す
    return send_from_directory('static', 'index.html')


@app.route("/api/stations", methods=["GET"])
def get_stations():
    """
    ?price_min=0&price_max=15&time_min=0&time_max=40 のようなクエリを受け取り
    stationsテーブルをフィルタして返す。
    """
    price_min = float(request.args.get("price_min", 0))
    price_max = float(request.args.get("price_max", 999999))
    time_min = int(request.args.get("time_min", 0))
    time_max = int(request.args.get("time_max", 999999))

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    SELECT line, station, lat, lng, price, commute_time
    FROM stations
    WHERE price BETWEEN %s AND %s
      AND commute_time BETWEEN %s AND %s
    """
    cur.execute(sql, (price_min, price_max, time_min, time_max))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    # レスポンスはJSON
    data = []
    for r in rows:
        data.append({
            "line": r[0],
            "station": r[1],
            "lat": r[2],
            "lng": r[3],
            "price": r[4],
            "commute_time": r[5]
        })
    return jsonify(data)


if __name__ == "__main__":
    port = 5000
    app.run(debug=True, host="0.0.0.0", port=port)
