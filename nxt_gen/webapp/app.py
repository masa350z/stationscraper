"""
シンプルなFlask Webアプリケーション
CSVファイルを読み込んで地図上に駅情報を表示
"""
from flask import Flask, render_template, jsonify, request
import pandas as pd
import os

app = Flask(__name__)

# データファイルのパス
DATA_FILE = "../data/stations_complete.csv"
FILTERED_DATA_FILE = "../data/filtered_stations_complete.csv"

def load_station_data(use_filtered=False):
    """
    駅データをCSVから読み込み

    Parameters:
    -----------
    use_filtered : bool
        フィルタ済みデータを使用するか

    Returns:
    --------
    list : 駅データのリスト
    """
    file_path = FILTERED_DATA_FILE if use_filtered else DATA_FILE

    if not os.path.exists(file_path):
        # ファイルが存在しない場合は空のリストを返す
        return []

    try:
        df = pd.read_csv(file_path)

        # NaNを適切な値に置換
        df['price'] = df['price'].fillna(0)
        df['total_min'] = df['total_min'].fillna(999) if 'total_min' in df.columns else 999
        df['trans'] = df['trans'].fillna(0) if 'trans' in df.columns else 0

        # 辞書のリストに変換
        stations = []
        for _, row in df.iterrows():
            station = {
                'line': row['line'],
                'station': row['station'],
                'lat': row['lat'],
                'lng': row['lng'],
                'price': float(row['price']) if row['price'] > 0 else None,
            }

            # 経路情報がある場合は追加
            if 'to_station' in df.columns and pd.notna(row.get('to_station')):
                station['to_station'] = row['to_station']
                station['total_min'] = int(row['total_min'])
                station['trans'] = int(row['trans'])
                station['train_min'] = int(row['train_min']) if 'train_min' in row else None
                station['walk_min'] = int(row['walk_min']) if 'walk_min' in row else None

            stations.append(station)

        return stations
    except Exception as e:
        print(f"データ読み込みエラー: {e}")
        return []

@app.route('/')
def index():
    """
    メインページを表示
    """
    return render_template('index.html')

@app.route('/api/stations')
def get_stations():
    """
    駅データをJSON形式で返すAPI

    クエリパラメータ:
    - max_price: 最大家賃（万円）
    - max_time: 最大所要時間（分）
    - max_trans: 最大乗り換え回数
    """
    # クエリパラメータを取得
    max_price = request.args.get('max_price', type=float)
    max_time = request.args.get('max_time', type=int)
    max_trans = request.args.get('max_trans', type=int)

    # データを読み込み
    stations = load_station_data()

    # フィルタリング
    if max_price is not None:
        stations = [s for s in stations if s['price'] is None or s['price'] <= max_price]

    if max_time is not None:
        stations = [s for s in stations if 'total_min' not in s or s['total_min'] <= max_time]

    if max_trans is not None:
        stations = [s for s in stations if 'trans' not in s or s['trans'] <= max_trans]

    return jsonify(stations)

@app.route('/api/stats')
def get_stats():
    """
    データの統計情報を返すAPI
    """
    stations = load_station_data()

    if not stations:
        return jsonify({
            'total': 0,
            'with_price': 0,
            'with_route': 0
        })

    with_price = sum(1 for s in stations if s['price'] is not None)
    with_route = sum(1 for s in stations if 'to_station' in s)

    return jsonify({
        'total': len(stations),
        'with_price': with_price,
        'with_route': with_route
    })

if __name__ == '__main__':
    print("=" * 60)
    print("nxt_gen Web アプリケーション起動")
    print("=" * 60)
    print("\nブラウザで以下のURLにアクセスしてください:")
    print("http://localhost:5001")
    print("\n終了するには Ctrl+C を押してください")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5001)