"""
frontend - シンプルなFlask Webアプリケーション

filtered_master_toranomon_common_2k.csv を単一のマスターデータとして使用
CSVのカラム名をそのまま使用（変換なし）
"""
from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
from config import (
    CSV_PATH,
    DEFAULT_MAX_PRICE,
    DEFAULT_MAX_TIME,
    DEFAULT_MAX_TRANS,
    HOST,
    PORT,
    DEBUG,
    MAP_CENTER_LAT,
    MAP_CENTER_LNG,
    MAP_ZOOM
)

app = Flask(__name__)

def load_station_data():
    """
    駅データをCSVから読み込み

    CSVカラム: line, from, to, trans, min, lat, lng, price, walk_min
    追加計算: total_min = min + walk_min

    Returns:
    --------
    list : 駅データの辞書リスト
    """
    if not os.path.exists(CSV_PATH):
        print(f"エラー: CSVファイルが見つかりません: {CSV_PATH}")
        return []

    try:
        # CSVを読み込み
        df = pd.read_csv(CSV_PATH)

        # total_min を計算（電車時間 + 徒歩時間）
        df['total_min'] = df['min'] + df['walk_min']

        # NaNを適切な値に置換
        df['price'] = df['price'].fillna(0)

        # 辞書のリストに変換
        stations = []
        for _, row in df.iterrows():
            station = {
                'line': row['line'],
                'from': row['from'],          # カラム名そのまま
                'to': row['to'],              # カラム名そのまま
                'lat': float(row['lat']),
                'lng': float(row['lng']),
                'price': float(row['price']) if row['price'] > 0 else None,
                'trans': int(row['trans']),
                'min': int(row['min']),       # 電車移動時間
                'walk_min': int(row['walk_min']),
                'total_min': int(row['total_min'])  # 合計時間
            }
            stations.append(station)

        print(f"データ読み込み完了: {len(stations)}駅")
        return stations

    except Exception as e:
        print(f"データ読み込みエラー: {e}")
        import traceback
        traceback.print_exc()
        return []

@app.route('/')
def index():
    """
    メインページを表示
    """
    return render_template(
        'index.html',
        map_center_lat=MAP_CENTER_LAT,
        map_center_lng=MAP_CENTER_LNG,
        map_zoom=MAP_ZOOM,
        default_max_price=DEFAULT_MAX_PRICE,
        default_max_time=DEFAULT_MAX_TIME,
        default_max_trans=DEFAULT_MAX_TRANS
    )

@app.route('/api/stations')
def get_stations():
    """
    駅データをJSON形式で返すAPI

    クエリパラメータ:
    - max_price: 最大家賃（万円）
    - max_time: 最大所要時間（分、電車+徒歩）
    - max_trans: 最大乗り換え回数

    Returns:
    --------
    JSON : フィルタリングされた駅データ
    """
    # クエリパラメータを取得（デフォルト値なし = フィルタなし）
    max_price = request.args.get('max_price', type=float)
    max_time = request.args.get('max_time', type=int)
    max_trans = request.args.get('max_trans', type=int)

    # データを読み込み
    stations = load_station_data()

    # フィルタリング
    if max_price is not None:
        stations = [s for s in stations if s['price'] is None or s['price'] <= max_price]

    if max_time is not None:
        stations = [s for s in stations if s['total_min'] <= max_time]

    if max_trans is not None:
        stations = [s for s in stations if s['trans'] <= max_trans]

    return jsonify(stations)

@app.route('/api/stats')
def get_stats():
    """
    データの統計情報を返すAPI

    Returns:
    --------
    JSON : 統計情報（全駅数、家賃情報あり駅数、平均家賃、平均所要時間）
    """
    stations = load_station_data()

    if not stations:
        return jsonify({
            'total': 0,
            'with_price': 0,
            'avg_price': 0,
            'avg_time': 0
        })

    # 統計計算
    with_price = [s for s in stations if s['price'] is not None]
    avg_price = sum(s['price'] for s in with_price) / len(with_price) if with_price else 0
    avg_time = sum(s['total_min'] for s in stations) / len(stations)

    return jsonify({
        'total': len(stations),
        'with_price': len(with_price),
        'avg_price': round(avg_price, 1),
        'avg_time': round(avg_time, 1)
    })

if __name__ == '__main__':
    print("=" * 60)
    print("frontend - 駅情報マップ Webアプリケーション起動")
    print("=" * 60)
    print(f"\nデータソース: {CSV_PATH}")
    print(f"\nブラウザで以下のURLにアクセスしてください:")
    print(f"http://localhost:{PORT}")
    print("\n終了するには Ctrl+C を押してください")
    print("=" * 60)

    app.run(debug=DEBUG, host=HOST, port=PORT)
