import pandas as pd
import os

from src.scrapers.traveltowns_scraper import scrape_traveltowns_kanto
from src.scrapers.suumo_scraper import scrape_suumo_2ldk_rent

from src.apis.ekispert import get_minimum_route_info_between_stations
from src.apis.google_maps import geocode_location

from src.pipeline.data_cleaning import merge_station_info, add_walking_time
from src.pipeline.data_cleaning import filter_station_data
from src.pipeline.analysis import evaluate_and_split
from src.pipeline.visualization import plot_scatter

from src.config import WALK_MINUTES, MAX_TIME_DEFAULT


def main():
    """
    全体のエントリーポイントとなるメイン関数。
    """

    # 1. スクレイピング（Traveltowns）
    data_dir = "data"
    station_address_csv = os.path.join(data_dir, "station_address.csv")
    if not os.path.exists(station_address_csv):
        print("[1] Traveltownsから駅マスタを取得...")
        scrape_traveltowns_kanto(station_address_csv)
    else:
        print("[1] 駅マスタCSVが既に存在します:", station_address_csv)

    # 2. スクレイピング（SUUMO家賃2LDK）
    station_price_csv = os.path.join(data_dir, "station_price_2ldk.csv")
    if not os.path.exists(station_price_csv):
        print("[2] SUUMOから家賃相場(2LDK)を取得...")
        pref_list = ['tokyo', 'kanagawa', 'saitama', 'chiba']
        scrape_suumo_2ldk_rent(pref_list, station_price_csv)
    else:
        print("[2] 家賃相場CSVが既に存在します:", station_price_csv)

    # 3. 駅マスタと家賃CSVを結合
    merged_csv = os.path.join(data_dir, "output", "station_info.csv")
    if not os.path.exists(merged_csv):
        print("[3] 駅マスタと家賃をマージ...")
        merge_station_info(station_address_csv, station_price_csv, merged_csv)
    else:
        print("[3] station_info.csv が既に存在:", merged_csv)

    # 4. 各駅から特定目的地(例: 渋谷)までの所要時間をEkispertで取得 -> CSVにまとめる
    route_csv = os.path.join(data_dir, "output", "route_info.csv")
    if not os.path.exists(route_csv):
        print("[4] Ekispertで所要時間を取得...")
        _calculate_min_route(merged_csv, "渋谷", route_csv)
    else:
        print("[4] route_info.csv が既に存在:", route_csv)

    # 5. 徒歩時間を加算して train+walk_min を作成
    df_route = pd.read_csv(route_csv)
    df_route = add_walking_time(df_route, WALK_MINUTES, to_col='to', time_col='min', new_col='train+walk_min')
    df_route.to_csv(route_csv, index=False)
    print("[5] 徒歩時間を加算しました。")

    # 6. フィルタリング（例えば "所要時間 <= 60分" など）
    filtered_csv = os.path.join(data_dir, "output", "filtered.csv")
    filter_station_data(route_csv, time_threshold=60, price_threshold=30, output_csv=filtered_csv)

    # 7. 絞り込み結果をさらに解析してファイルを分割保存
    evaluate_and_split(filtered_csv, os.path.join(data_dir, "output"))

    # 8. Google Maps Geocodingで各駅に緯度経度を付与
    merged_with_geo_csv = os.path.join(data_dir, "output", "merged_with_coordinates.csv")
    if not os.path.exists(merged_with_geo_csv):
        _append_geocode(filtered_csv, merged_with_geo_csv)
    else:
        print("[8] merged_with_coordinates.csv が既に存在:", merged_with_geo_csv)

    # 9. 可視化
    figure_path = os.path.join(data_dir, "output", "figure.png")
    plot_scatter(file_path=merged_with_geo_csv,
                 lat_col='lat',
                 lng_col='lng',
                 color_col='price',
                 lat_min=35.5,
                 lat_max=35.9,
                 lng_min=139.4,
                 lng_max=140.0,
                 cmap_min=0,
                 cmap_max=40,
                 marker_size=80,
                 alpha=0.7,
                 resolution=(1920, 1080),
                 output_file=figure_path)

    print("すべての処理が完了しました。")


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
        route_info = get_minimum_route_info_between_stations(from_station, to_station)
        if route_info is None:
            continue
        trans, minutes = route_info
        records.append([line, price, from_station, to_station, trans, minutes])

    out_df = pd.DataFrame(records, columns=['line', 'price', 'from', 'to', 'trans', 'min'])
    out_df.to_csv(output_csv, index=False)
    print(f"最短ルート情報を保存: {output_csv}")


def _append_geocode(input_csv: str, output_csv: str) -> None:
    """
    フィルタ済のCSVに緯度経度情報を付与して書き出す。
    """
    from src.apis.google_maps import geocode_location

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


if __name__ == "__main__":
    main()