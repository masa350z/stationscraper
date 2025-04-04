import requests
from bs4 import BeautifulSoup
import numpy as np

from src.config import EKISPERT_KEY


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


def get_course_resource_uri(from_station: str, to_station: str) -> str or None:
    """
    2駅間のコース検索用のResourceURIを取得。
    見つからない場合はNone。
    """
    url = 'https://api.ekispert.jp/v1/json/search/course/light'
    from_name = get_official_station_name(from_station)
    to_name = get_official_station_name(to_station)
    if not from_name or not to_name:
        return None

    params = {
        'key': EKISPERT_KEY,
        'from': from_name,
        'to': to_name,
        'time': '0900',
        'searchType': 'arrival'
    }
    res = requests.get(url, params=params).json()
    if 'ResultSet' not in res or 'ResourceURI' not in res['ResultSet']:
        return None
    return res['ResultSet']['ResourceURI']


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
    """
    uri = get_course_resource_uri(from_station, to_station)
    if not uri:
        return None
    return get_minimum_route_info(uri)