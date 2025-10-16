"""
Ekispert APIを使用した経路情報収集モジュール
src/apis/ekispert.pyのコードをそのまま使用
"""
import requests
from bs4 import BeautifulSoup
import numpy as np
import time
import pandas as pd
from config import EKISPERT_KEY, API_SLEEP_SEC


def get_official_station_name(station_name: str) -> str or None:
    """
    引数の駅名に対してEkispert APIを呼び出し、
    正式な駅名を返す。見つからない場合はNone。
    """
    url = 'https://api.ekispert.jp/v1/json/station'
    params = {
        'key': EKISPERT_KEY,
        'name': station_name
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


def get_station_code(station_name: str) -> str or None:
    """
    駅名から駅コードを取得
    """
    url = 'https://api.ekispert.jp/v1/json/station'
    params = {
        'key': EKISPERT_KEY,
        'name': station_name
    }
    res = requests.get(url, params=params).json()
    if 'ResultSet' not in res:
        return None
    data = res['ResultSet'].get('Point')
    if not data:
        return None

    if isinstance(data, list):
        return data[0]['Station'].get('code')
    else:
        return data['Station'].get('code')


def get_course_resource_uri(from_station: str, to_station: str) -> str or None:
    """
    2駅間のコース検索用のURLを直接構築
    新しいroote.ekispert.netの形式に対応
    """
    from_name = get_official_station_name(from_station)
    to_name = get_official_station_name(to_station)
    if not from_name or not to_name:
        return None

    # 駅コードを取得
    from_code = get_station_code(from_station)
    to_code = get_station_code(to_station)

    if not from_code or not to_code:
        return None

    # URLを直接構築（新形式）
    import urllib.parse
    base_url = 'https://roote.ekispert.net/result'
    params = {
        'ticketType': 'IC',
        'surchargeType': 'non_reserved',
        'transferTime': 'normal',
        'sort': 'time',
        'searchType': 'arrival',
        'shinkansen': 'true',
        'express': 'true',
        'highway': 'true',
        'local': 'true',
        'plane': 'true',
        'ship': 'true',
        'sleep': 'false',
        'liner': 'true',
        'isRealtime': 'false',
        'depName': from_name,
        'arrName': to_name,
        'depCode': from_code,
        'arrCode': to_code,
        'dateTime': '1757808050'  # 固定値で問題ないはず
    }

    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"


def get_minimum_route_info(resource_uri: str) -> tuple or None:
    """
    ResourceURIを元にEkispertのページをパースし、
    乗り換え回数が最小、かつ所要時間が最小となるものを返す。
    戻り値: (乗り換え回数, 所要時間(分)) or None
    """
    if not resource_uri:
        return None

    res = requests.get(resource_uri)
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find('div', id='tabs_color')
    if not table:
        return None

    rows = table.find_all('tr')
    candidate_list = []
    for row in rows:
        p_tags = row.find_all('p', class_="candidate_list_txt")
        if len(p_tags) < 2:
            continue

        # 所要時間のパース
        time_str = p_tags[0].find('span').text
        # time_strの末尾に「（XX分）」の形が入っている
        # 例: "乗車XX分（1時間25分）" のようなパターンを想定
        if '（' in time_str and '）' in time_str:
            inner = time_str.split('（')[-1].replace('）', '')
            required_minutes = parse_time_str(inner)
        else:
            continue

        # 乗り換え回数のパース
        transfer_str = p_tags[1].find('span').text
        try:
            transfer_count = int(transfer_str.replace('回', ''))
        except ValueError:
            transfer_count = 999  # 不明の場合は大きな数字

        candidate_list.append((transfer_count, required_minutes))

    if not candidate_list:
        return None

    arr = np.array(candidate_list)
    # 乗り換え回数が最小の要素群をフィルタ
    min_trans = arr[arr[:, 0] == np.min(arr[:, 0])]
    # さらに所要時間が最小のものを取る
    min_minute = min_trans[min_trans[:, 1] == np.min(min_trans[:, 1])][0]
    return (int(min_minute[0]), int(min_minute[1]))


def parse_time_str(time_str: str) -> int:
    """
    "1時間25分" のような文字列を総分数(int)に変換する。
    """
    hour = 0
    minute = 0
    if '時間' in time_str:
        parts = time_str.split('時間')
        hour_part = parts[0]
        hour = int(hour_part) if hour_part.isdigit() else 0
        minute_part = parts[1].replace('分', '').strip()
        minute = int(minute_part) if minute_part.isdigit() else 0
    else:
        # 例 "45分"
        minute = int(time_str.replace('分', ''))
    return hour * 60 + minute


def get_minimum_route_info_between_stations(from_station: str, to_station: str) -> tuple or None:
    """
    from_station->to_stationの最適ルート情報(乗り換え最小・所要時間最小)を返す
    /search/course API（簡易探索）を使用
    """
    # まず駅名を正規化
    from_name = get_official_station_name(from_station)
    to_name = get_official_station_name(to_station)

    if not from_name or not to_name:
        return None

    # /search/course API を使用（これは利用可能）
    url = 'https://api.ekispert.jp/v1/json/search/course'
    params = {
        'key': EKISPERT_KEY,
        'from': from_name,
        'to': to_name,
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

                    # 所要時間（乗車時間 + その他時間）
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
        # デバッグ用（本番では削除）
        # print(f"Error for {from_station} -> {to_station}: {e}")
        pass

    return None


# nxt_gen用の追加関数
def get_route_info_between_stations(from_station: str, to_station: str) -> tuple or None:
    """
    from_station->to_stationの最適ルート情報を返す
    (get_minimum_route_info_between_stationsのエイリアス)
    """
    return get_minimum_route_info_between_stations(from_station, to_station)


def collect_route_info(df_stations, target_station, walk_minutes):
    """
    各駅から対象駅への経路情報を収集

    Parameters:
    -----------
    df_stations : pandas.DataFrame
        駅データ（station列が必要）
    target_station : str
        目的地駅名
    walk_minutes : int
        駅からの徒歩時間（分）

    Returns:
    --------
    pandas.DataFrame : 経路情報を含むデータフレーム
    """
    records = []
    total_stations = len(df_stations)

    print(f"\n{target_station}への経路情報を収集中...")

    for idx, row in df_stations.iterrows():
        from_station = row['station']

        # 進捗表示
        if (idx + 1) % 10 == 0:
            print(f"  進捗: {idx + 1}/{total_stations} ({(idx + 1)/total_stations*100:.1f}%)")

        # API呼び出し
        route_info = get_minimum_route_info_between_stations(from_station, target_station)

        if route_info is None:
            continue

        trans, minutes = route_info
        total_minutes = minutes + walk_minutes  # 徒歩時間を加算

        record = {
            'line': row['line'],
            'station': from_station,
            'to_station': target_station,
            'trans': trans,
            'train_min': minutes,
            'walk_min': walk_minutes,
            'total_min': total_minutes
        }
        records.append(record)

        # API負荷軽減のためスリープ
        time.sleep(API_SLEEP_SEC)

    print(f"  収集完了: {len(records)}件の経路情報")

    return pd.DataFrame(records)