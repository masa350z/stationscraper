import csv
import psycopg2
import time
import os

# DB接続情報
DB_HOST = os.environ.get("DB_HOST", "db")  # docker-compose上のサービス名"db"
DB_USER = os.environ.get("POSTGRES_USER", "stationuser")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "stationpass")
DB_NAME = os.environ.get("POSTGRES_DB", "stationdb")


def main():
    # DBに接続をリトライ(コンテナ起動直後はDBが起動中の場合あり)
    for i in range(10):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=DB_NAME
            )
            break
        except Exception as e:
            print("DB接続失敗...リトライ", e)
            time.sleep(3)
    else:
        raise RuntimeError("PostgreSQLへの接続に失敗しました。")

    cur = conn.cursor()

    # stationsテーブルを作成（存在しない場合のみ）
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS stations (
        id SERIAL PRIMARY KEY,
        line TEXT,
        station TEXT,
        lat DOUBLE PRECISION,
        lng DOUBLE PRECISION,
        price DOUBLE PRECISION,
        commute_time INT
    );
    """
    cur.execute(create_table_sql)
    conn.commit()

    # CSVを読み込んでINSERT
    with open("stations.csv", mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # いったんテーブルを空にする（再起動時に重複INSERTしないため）
    cur.execute("TRUNCATE stations;")
    conn.commit()

    insert_sql = """
    INSERT INTO stations (line, station, lat, lng, price, commute_time)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    for row in rows:
        cur.execute(insert_sql, (
            row["line"],
            row["station"],
            float(row["lat"]),
            float(row["lng"]),
            float(row["price"]),
            int(row["commute_time"])
        ))
    conn.commit()
    print("init_db.py: CSVデータをstationsテーブルに投入完了")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
