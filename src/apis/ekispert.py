import requests

from config import EKISPERT_KEY


def get_official_station_name(station_name: str) -> str or None:
    """
    引数の駅名に対してEkispert APIを呼び出し、
    正式な駅名を返す。見つからない場合はNone。
    電車の駅のみを検索対象とする（バス停を除外）。
    """
    url = 'https://api.ekispert.jp/v1/json/station'
    params = {
        'key': EKISPERT_KEY,
        'name': station_name,
        'type': 'train'  # 電車の駅のみ検索
    }
    res = requests.get(url, params=params).json()
    if 'ResultSet' not in res:
        return None
    data = res['ResultSet'].get('Point')
    if not data:
        return None

    if isinstance(data, list):
        # 複数駅候補が返るケース
        return data[0]['Station']['Name']
    else:
        return data['Station']['Name']


def get_minimum_route_info_between_stations(from_station: str, to_station: str) -> tuple or None:
    """
    from_station->to_stationの最適ルート情報(乗り換え最小・所要時間最小)を返す
    /search/course API（lightなし）を使用してJSON APIレスポンスから直接取得
    戻り値: (乗り換え回数, 所要時間(分)) or None
    """
    # まず駅名を正規化（失敗したら元の駅名を使う）
    from_name = get_official_station_name(from_station) or from_station
    to_name = get_official_station_name(to_station) or to_station

    # /search/course API を使用（lightなし - これが正しいエンドポイント）
    url = 'https://api.ekispert.jp/v1/json/search/course'
    params = {
        'key': EKISPERT_KEY,
        'from': from_name,
        'to': to_name,
        'time': '0900',         # 朝9時を指定（通勤時間帯）
        'searchType': 'arrival',  # 9時到着のルートを検索
        'plane': 'false',  # 飛行機は使わない
        'bus': 'false'      # バスも使わない（電車のみ）
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if 'ResultSet' in data and 'Course' in data['ResultSet']:
                courses = data['ResultSet']['Course']
                # 単一のコースの場合はリスト化
                if not isinstance(courses, list):
                    courses = [courses]

                # 各コースから乗換回数と所要時間を抽出
                candidates = []
                for course in courses:
                    route = course.get('Route', {})

                    # 乗換回数
                    transfer_count = int(route.get('transferCount', 0))

                    # 所要時間（乗車時間 + その他時間 + 徒歩時間）
                    time_on_board = int(route.get('timeOnBoard', 0))
                    time_other = int(route.get('timeOther', 0))
                    time_walk = int(route.get('timeWalk', 0))
                    time_total = time_on_board + time_other + time_walk

                    if time_total > 0:
                        candidates.append((transfer_count, time_total))

                if candidates:
                    # 乗換回数が最小、かつ所要時間が最小のものを選択
                    candidates.sort(key=lambda x: (x[0], x[1]))
                    return candidates[0]
    except Exception as e:
        # エラーが発生した場合はNoneを返す
        pass

    return None