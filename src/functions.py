# %%
"""
データパイプライン処理用の関数群

このモジュールは駅データ、家賃データ、経路情報の取得・マージ処理を行う関数を提供する。
"""
import pandas as pd
import os

from scrapers.traveltowns_scraper import scrape_traveltowns_kanto
from scrapers.suumo_scraper import scrape_suumo_rent

from apis.ekispert import get_minimum_route_info_between_stations

from pipeline.data_cleaning import add_walking_time

from config import WALK_MINUTES
from config import ROOM_TYPE


def _calculate_min_route(df: pd.DataFrame, to_station: str, output_csv: str) -> pd.DataFrame:
    """
    駅一覧DataFrameから各駅->to_stationまでの最小乗り換え回数・所要時間を取得する。

    Args:
        df: 駅一覧DataFrame (line, station, price列を含む)
        to_station: 目的地の駅名
        output_csv: 結果を保存するCSVファイルパス

    Returns:
        pd.DataFrame: 経路情報DataFrame (line, price, from, to, trans, min列)
    """
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

    return out_df


def geocode_station(line: str, station: str) -> tuple:
    """
    複数のクエリパターンで座標取得を試行する汎用的な関数。

    複数の検索パターンを順に試行することで、座標取得の成功率を向上させる。

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


def make_station_master() -> pd.DataFrame:
    """
    駅マスタを作成する。
    既に存在する場合は既存ファイルから読み込む。

    Returns:
        pd.DataFrame: 駅マスタDataFrame (line, station列を含む)
    """
    data_dir = "../data"
    station_address_csv = os.path.join(data_dir, "station_master", "station_address.csv")

    if not os.path.exists(station_address_csv):
        print("[1] Traveltownsから駅マスタを取得...")
        scrape_traveltowns_kanto(station_address_csv)
    else:
        print("[1] 駅マスタCSVが既に存在します:", station_address_csv)

    # CSVを読み込んでDataFrameとして返す
    df = pd.read_csv(station_address_csv)
    return df


def make_rent_data() -> pd.DataFrame:
    """
    家賃相場データを作成する。
    既に存在する場合は既存ファイルから読み込む。

    Returns:
        pd.DataFrame: 家賃相場DataFrame
    """
    data_dir = "../data"
    station_price_csv = os.path.join(
        data_dir, "price_by_station", f"price_by_station_{ROOM_TYPE}.csv")

    if not os.path.exists(station_price_csv):
        print(f"[2] SUUMOから家賃相場({ROOM_TYPE})を取得...")
        pref_list = ['tokyo', 'kanagawa', 'saitama', 'chiba']
        scrape_suumo_rent(pref_list, station_price_csv, room_type=ROOM_TYPE)
    else:
        print("[2] 家賃相場CSVが既に存在します:", station_price_csv)

    # CSVを読み込んでDataFrameとして返す
    df = pd.read_csv(station_price_csv)
    return df


def add_geocode_to_station_master(df: pd.DataFrame, output_csv: str) -> pd.DataFrame:
    """
    駅マスタDataFrameに座標情報を付与する。

    既存の座標データ（output_csv）があれば読み込んで活用し、
    座標がない駅だけ新規取得することでAPI使用量を節約する。

    Args:
        df: 駅マスタDataFrame (line, station列を含む)
        output_csv: 座標付き駅マスタCSVの出力パス (line, station, lat, lng)

    Returns:
        pd.DataFrame: 座標付き駅マスタDataFrame (line, station, lat, lng列を含む)
    """
    import time

    # 駅マスタをコピー
    df_stations = df.copy()

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
        return df_merged

    print(f"[2] 座標が欠損している駅: {missing_count}駅")
    print(f"[2] Google Maps APIで座標を取得します...")

    # 座標を取得
    success_count = 0
    for idx, row in missing_coords.iterrows():
        line = row['line']
        station = row['station']

        # 複数パターンで座標取得を試行
        lat, lng = geocode_station(line, station)

        # DataFrameを更新
        df_merged.loc[idx, 'lat'] = lat
        df_merged.loc[idx, 'lng'] = lng

        if lat is not None and lng is not None:
            success_count += 1

        # 進捗表示（10駅ごと）
        current = success_count + (len(missing_coords) - missing_count + len(missing_coords[:idx + 1]))
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
    return df_merged


def make_merged_data(station_df: pd.DataFrame, price_df: pd.DataFrame) -> pd.DataFrame:
    """
    駅マスタと家賃データをマージする。
    路線名の表記揺れを正規化してからマージを行う。

    Args:
        station_df: 駅マスタDataFrame (line, station, lat, lng列を含む)
        price_df: 家賃相場DataFrame (line, station, price列を含む)

    Returns:
        pd.DataFrame: マージ済みDataFrame (line, station, lat, lng, price列を含む)
    """
    from pipeline.data_cleaning import normalize_line_names

    print("[3] 駅マスタと家賃をマージ...")

    # 路線名を正規化（全角JR→半角、小田急線の分割など）
    price_df_normalized = normalize_line_names(price_df, station_df)

    # 駅マスタをベースに左結合（座標情報を保持）
    merged = pd.merge(station_df, price_df_normalized, on=['line', 'station'], how='left')
    merged.drop_duplicates(inplace=True)

    # 統計情報を出力
    total = len(merged)
    with_price = merged['price'].notna().sum()
    print(f"  総駅数: {total}")
    print(f"  価格データあり: {with_price} ({with_price/total*100:.1f}%)")
    print(f"  価格データなし: {total - with_price} ({(total - with_price)/total*100:.1f}%)")

    return merged


def make_route_data(merged_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    各目的地への経路情報を取得する。
    既に保存済みデータがある場合は既存ファイルから読み込む。
    徒歩時間も加算して返す。

    Args:
        merged_df: マージ済みDataFrame（駅マスタ+家賃）

    Returns:
        dict[str, pd.DataFrame]: 目的地名をキーとした経路情報DataFrameのdict
    """
    data_dir = "../data"
    route_data_dict = {}

    for to_station in WALK_MINUTES.keys():
        route_csv = os.path.join(
            data_dir, "output", "route_info", f"route_info_{to_station}.csv")

        if not os.path.exists(route_csv):
            print(f"[4] Ekispertで{to_station}への所要時間を取得...")
            df_route = _calculate_min_route(merged_df, to_station, route_csv)
        else:
            print(f"[4] route_info_{to_station}.csv が既に存在:", route_csv)
            df_route = pd.read_csv(route_csv)

        # 徒歩時間を加算
        df_route = add_walking_time(
            df_route, WALK_MINUTES, to_col='to', time_col='min', new_col='train+walk_min')
        # 保存
        df_route.to_csv(route_csv, index=False)
        print(f"[5] {to_station}への徒歩時間を加算しました。")

        # dictに追加
        route_data_dict[to_station] = df_route

    return route_data_dict


def merge_all_route_data(route_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    全目的地の経路情報を1つのDataFrameに統合する。

    Args:
        route_dict: 目的地名をキーとした経路情報DataFrameのdict

    Returns:
        pd.DataFrame: 統合されたDataFrame
    """
    data_dir = "../data"
    merged_csv_path = os.path.join(
        data_dir, "output", "merged", f"merged_info_{ROOM_TYPE}.csv")

    # dictの全DataFrameを結合
    merged_df = pd.concat(route_dict.values(), axis=0, ignore_index=True)

    # 保存
    merged_df.to_csv(merged_csv_path, index=False)
    print("[6] 全経路情報を結合しました:", merged_csv_path)

    return merged_df
