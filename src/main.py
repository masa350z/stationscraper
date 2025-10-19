# %%
import pandas as pd
import os

from scrapers.traveltowns_scraper import scrape_traveltowns_kanto
from scrapers.suumo_scraper import scrape_suumo_rent

from apis.ekispert import get_minimum_route_info_between_stations

from pipeline.data_cleaning import merge_station_info, add_walking_time

from config import WALK_MINUTES
from config import ROOM_TYPE

# %%


def _calculate_min_route(station_csv: str, to_station: str, output_csv: str) -> None:
    """
    駅一覧CSVを読み込み、各駅->to_stationまでの最小乗り換え回数・所要時間を取得してCSVにまとめる。
    """
    df = pd.read_csv(station_csv)
    records = []
    for idx, row in df.iterrows():
        from_station = row['station']
        line = row['line']
        price = row['price']
        if pd.isna(price):
            continue
        # Ekispert呼び出し
        route_info = get_minimum_route_info_between_stations(
            from_station, to_station)
        if route_info is None:
            continue
        trans, minutes = route_info
        print([line, price, from_station, to_station, trans, minutes])
        records.append([line, price, from_station, to_station, trans, minutes])

    out_df = pd.DataFrame(
        records, columns=['line', 'price', 'from', 'to', 'trans', 'min'])
    out_df.to_csv(output_csv, index=False)
    print(f"最短ルート情報を保存: {output_csv}")


def geocode_station_with_retry(line: str, station: str) -> tuple:
    """
    複数のクエリパターンで座標取得を試行する汎用的な関数。

    複数の検索パターンを順に試行することで、座標取得の成功率を向上させる。
    geocode_missing_stations.py のロジックを本質的に抽出。

    Args:
        line: 路線名 (例: "JR山手線")
        station: 駅名 (例: "新宿")

    Returns:
        tuple: (lat, lng) 座標取得成功時、(None, None) 失敗時
    """
    from apis.google_maps import geocode_location
    import time

    # 複数の検索クエリパターンを定義
    query_patterns = [
        f"{line} {station}駅",      # パターン1: "XX線 XX駅"
        f"{line} {station}",         # パターン2: "XX線 XX" (駅を外す)
        f"{station}駅",              # パターン3: "XX駅" (路線名を外す)
        f"{station}",                # パターン4: "XX" (駅も路線名も外す)
    ]

    # 各パターンを順番に試行
    for query in query_patterns:
        lat, lng = geocode_location(query)
        if lat is not None and lng is not None:
            return (lat, lng)
        time.sleep(0.5)  # 失敗時も少し待機

    return (None, None)


def _append_geocode(input_csv: str, output_csv: str) -> None:
    """
    フィルタ済のCSVに緯度経度情報を付与して書き出す。
    """
    from apis.google_maps import geocode_location

    df = pd.read_csv(input_csv)
    lat_list = []
    lng_list = []
    for station_name in df['from']:
        # 駅名+駅 で検索
        query = f"{station_name}駅"
        lat, lng = geocode_location(query)
        lat_list.append(lat if lat else 0)
        lng_list.append(lng if lng else 0)

    df['lat'] = lat_list
    df['lng'] = lng_list
    df.to_csv(output_csv, index=False)
    print(f"ジオコード結果を付与: {output_csv}")


# %%
# パイプライン実行用のヘルパー関数群


def make_station_master() -> str:
    """
    駅マスタCSVを作成する。
    既に存在する場合は既存ファイルを使用する。

    Returns:
        str: 駅マスタCSVのパス
    """
    data_dir = "../data"
    station_address_csv = os.path.join(data_dir, "station_address.csv")

    if not os.path.exists(station_address_csv):
        print("[1] Traveltownsから駅マスタを取得...")
        scrape_traveltowns_kanto(station_address_csv)
    else:
        print("[1] 駅マスタCSVが既に存在します:", station_address_csv)

    return station_address_csv


def make_rent_data() -> str:
    """
    家賃相場CSVを作成する。
    既に存在する場合は既存ファイルを使用する。

    Returns:
        str: 家賃相場CSVのパス
    """
    data_dir = "../data"
    station_price_csv = os.path.join(
        data_dir, "station_price", f"station_price_{ROOM_TYPE}.csv")

    if not os.path.exists(station_price_csv):
        print(f"[2] SUUMOから家賃相場({ROOM_TYPE})を取得...")
        pref_list = ['tokyo', 'kanagawa', 'saitama', 'chiba']
        scrape_suumo_rent(pref_list, station_price_csv, room_type=ROOM_TYPE)
    else:
        print("[2] 家賃相場CSVが既に存在します:", station_price_csv)

    return station_price_csv


def add_geocode_to_station_master(station_csv: str, output_csv: str) -> str:
    """
    駅マスタCSVに座標情報を付与して、座標付き駅マスタを作成する。

    既存の座標データ（output_csv）があれば読み込んで活用し、
    座標がない駅だけ新規取得することでAPI使用量を節約する。

    Args:
        station_csv: 駅マスタCSVのパス (line, station)
        output_csv: 座標付き駅マスタCSVの出力パス (line, station, lat, lng)

    Returns:
        str: 座標付き駅マスタCSVのパス
    """
    import time

    # 駅マスタを読み込む
    df_stations = pd.read_csv(station_csv)

    # 既存の座標データがあれば読み込む
    if os.path.exists(output_csv):
        print(f"[2] 既存の座標データを読み込みます: {output_csv}")
        df_existing = pd.read_csv(output_csv)
        # 既存データと新データをマージ（既存データを優先）
        df_merged = pd.merge(
            df_stations,
            df_existing,
            on=['line', 'station'],
            how='left'
        )
    else:
        print("[2] 座標データが存在しないため、新規作成します")
        df_merged = df_stations.copy()
        df_merged['lat'] = None
        df_merged['lng'] = None

    # 座標が欠損している駅を抽出
    missing_coords = df_merged[df_merged['lat'].isna()]
    missing_count = len(missing_coords)

    if missing_count == 0:
        print("[2] すべての駅に座標が付与されています")
        df_merged.to_csv(output_csv, index=False)
        return output_csv

    print(f"[2] 座標が欠損している駅: {missing_count}駅")
    print(f"[2] Google Maps APIで座標を取得します...")

    # 座標を取得
    success_count = 0
    for idx, row in missing_coords.iterrows():
        line = row['line']
        station = row['station']

        # 複数パターンで座標取得を試行
        lat, lng = geocode_station_with_retry(line, station)

        # DataFrameを更新
        df_merged.loc[idx, 'lat'] = lat
        df_merged.loc[idx, 'lng'] = lng

        if lat is not None and lng is not None:
            success_count += 1

        # 進捗表示（10駅ごと）
        current = success_count + (len(missing_coords) - missing_count + len(missing_coords[:idx+1]))
        if (current) % 10 == 0:
            failed = current - success_count
            print(f"    進捗: {current}/{missing_count} "
                  f"(成功: {success_count}, 失敗: {failed})")

        # API制限対策: 1秒待機
        time.sleep(1)

    # 結果を保存
    df_merged.to_csv(output_csv, index=False)

    # 統計情報を表示
    failed_count = missing_count - success_count
    print(f"[2] 座標取得完了: 成功 {success_count}/{missing_count} "
          f"({success_count/missing_count*100:.1f}%)")
    if failed_count > 0:
        print(f"    失敗した駅が {failed_count}駅 あります")

    print(f"[2] 座標付き駅マスタを保存: {output_csv}")
    return output_csv


def make_merged_data(station_csv: str, price_csv: str) -> str:
    """
    駅マスタと家賃データをマージしたCSVを作成する。
    既に存在する場合は既存ファイルを使用する。

    Args:
        station_csv: 駅マスタCSVのパス
        price_csv: 家賃相場CSVのパス

    Returns:
        str: マージ済みCSVのパス
    """
    data_dir = "../data"
    merged_csv = os.path.join(
        data_dir, "output", "price_info", f"price_by_station_{ROOM_TYPE}.csv")

    if not os.path.exists(merged_csv):
        print("[3] 駅マスタと家賃をマージ...")
        merge_station_info(station_csv, price_csv, merged_csv)
    else:
        print(f"[3] price_by_station_{ROOM_TYPE}.csv が既に存在:", merged_csv)

    return merged_csv


def make_route_data(merged_csv: str) -> None:
    """
    各目的地への経路情報CSVを作成する。
    既に存在する場合は既存ファイルを使用する。
    徒歩時間も加算して保存する。

    Args:
        merged_csv: マージ済みCSVのパス（駅マスタ+家賃）
    """
    data_dir = "../data"

    for to_station in WALK_MINUTES.keys():
        route_csv = os.path.join(
            data_dir, "output", "route_info", f"route_info_{to_station}.csv")

        if not os.path.exists(route_csv):
            print(f"[4] Ekispertで{to_station}への所要時間を取得...")
            _calculate_min_route(merged_csv, to_station, route_csv)
        else:
            print(f"[4] route_info_{to_station}.csv が既に存在:", route_csv)

        df_route = pd.read_csv(route_csv)
        df_route = add_walking_time(
            df_route, WALK_MINUTES, to_col='to', time_col='min', new_col='train+walk_min')
        df_route.to_csv(route_csv, index=False)
        print(f"[5] {to_station}への徒歩時間を加算しました。")


def merge_all_route_data() -> str:
    """
    全目的地の経路情報を1つのCSVに統合する。

    Returns:
        str: 統合CSVのパス
    """
    data_dir = "../data"
    merged_csv_path = os.path.join(
        data_dir, "output", "merged", f"merged_info_{ROOM_TYPE}.csv")
    merged_csv = pd.DataFrame()

    for to_station in WALK_MINUTES.keys():
        route_csv = os.path.join(
            data_dir, "output", "route_info", f"route_info_{to_station}.csv")
        df_route = pd.read_csv(route_csv)
        merged_csv = pd.concat([merged_csv, df_route], axis=0)

    merged_csv.to_csv(merged_csv_path, index=False)
    print("[6] 全経路情報を結合しました:", merged_csv_path)

    return merged_csv_path


# %%
data_dir = "../data"
station_address_csv = make_station_master()  # 駅マスタCSVを作成する
station_master_with_coords = add_geocode_to_station_master(
    station_address_csv,
    os.path.join(data_dir, "station_address_with_coordinates.csv")
)  # 駅マスタに座標情報を付与
station_price_csv = make_rent_data()  # 家賃相場CSVを作成する
merged_csv = make_merged_data(station_master_with_coords, station_price_csv)  # 座標付き駅マスタと家賃データをマージしたCSVを作成する
make_route_data(merged_csv)  # 各目的地への経路情報CSVを作成する
