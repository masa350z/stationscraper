"""
オフィスエリアごとのフロントエンド用マスターデータ生成スクリプト

このスクリプトは、make_base_data.pyで生成された駅データと経路データを使用して、
特定のオフィスエリア（虎ノ門、東京、大塚）ごとに最適化された
フロントエンド表示用のマスターデータを生成する。

前提条件:
- make_base_data.pyが実行済みであること
- data/station_coord_price/station_coord_price_{ROOM_TYPE}.csv が存在すること
- data/calculated_routes/calculated_routes_{駅名}.csv が存在すること

出力:
- data/frontend_master/frontend_master_{office}_{ROOM_TYPE}.csv
  (office: toranomon, tokyo, otsuka)
"""

import pandas as pd
import os
from config import (
    ROOM_TYPE,
    WALK_MINUTES,
    TO_TORANOMON_LIST,
    TO_TOKYO_LIST,
    TO_OTSUKA_LIST
)


def load_station_coord_price(data_dir):
    """
    駅の座標・価格情報を読み込む

    Args:
        data_dir: データディレクトリのパス

    Returns:
        DataFrame: 駅の座標・価格情報
    """
    path = os.path.join(
        data_dir,
        "station_coord_price",
        f"station_coord_price_{ROOM_TYPE}.csv"
    )
    return pd.read_csv(path)


def load_calculated_routes(data_dir, to_station_list):
    """
    指定された駅への経路データを読み込む

    Args:
        data_dir: データディレクトリのパス
        to_station_list: 目的駅のリスト

    Returns:
        dict: {駅名: DataFrame} の辞書
    """
    calculated_routes_dic = {}
    for to_station in to_station_list:
        path = os.path.join(
            data_dir,
            "calculated_routes",
            f"calculated_routes_{to_station}.csv"
        )
        calculated_routes_dic[to_station] = pd.read_csv(path)
    return calculated_routes_dic


def add_location_and_price_info(frontend_master, station_coord_price_df):
    """
    経路データに座標・価格・徒歩時間を追加する

    Args:
        frontend_master: 経路データのDataFrame
        station_coord_price_df: 駅の座標・価格情報

    Returns:
        DataFrame: 座標・価格・徒歩時間が追加されたDataFrame
    """
    additional_records = []

    for i in range(len(frontend_master)):
        row = frontend_master.iloc[i]

        # 駅情報を検索
        condition_line = station_coord_price_df['line'].str.contains(row['line'])
        condition_station = station_coord_price_df['station'].str.contains(row['from'])
        search_result = station_coord_price_df[condition_line & condition_station].iloc[0]

        # 必要な情報を抽出
        lat = search_result['lat']
        lng = search_result['lng']
        price = search_result['price']
        walk_min = WALK_MINUTES[row['to']]

        additional_records.append([lat, lng, price, walk_min])

    # 新しい列を追加
    additional_df = pd.DataFrame(
        additional_records,
        columns=['lat', 'lng', 'price', 'walk_min']
    )
    return pd.concat([frontend_master, additional_df], axis=1)


def make_frontend_master_for_office(office_name, to_station_list, calculated_routes_dic, station_coord_price_df, data_dir):
    """
    特定オフィスエリア向けのフロントエンドマスターデータを生成

    Args:
        office_name: オフィス名 ('toranomon', 'tokyo', 'otsuka')
        to_station_list: そのオフィスへの通勤に使う駅のリスト
        calculated_routes_dic: 経路データの辞書
        station_coord_price_df: 駅の座標・価格情報
        data_dir: データディレクトリのパス

    Returns:
        DataFrame: 生成されたフロントエンドマスターデータ
    """
    # 1. 該当する駅の経路データを統合
    frontend_master = pd.DataFrame({})
    for to_station in to_station_list:
        frontend_master = pd.concat(
            [frontend_master, calculated_routes_dic[to_station]],
            ignore_index=True
        )

    # 2. 座標・価格・徒歩時間を追加
    frontend_master = add_location_and_price_info(frontend_master, station_coord_price_df)

    # 3. ファイルに保存
    output_path = os.path.join(
        data_dir,
        "frontend_master",
        f"frontend_master_{office_name}_{ROOM_TYPE}.csv"
    )
    frontend_master.to_csv(output_path, index=False)
    print(f"✓ 生成完了: {output_path}")

    return frontend_master


def main():
    """
    メイン処理: 全オフィスエリアのフロントエンドマスターデータを生成
    """
    data_dir = "../data"

    print("=" * 60)
    print("フロントエンドマスターデータ生成開始")
    print("=" * 60)

    # 1. 基礎データの読み込み
    print("\n[1/3] 基礎データを読み込み中...")
    station_coord_price_df = load_station_coord_price(data_dir)
    print(f"  - 駅データ: {len(station_coord_price_df)} 件")

    # 2. 全目的駅の経路データを読み込み
    print("\n[2/3] 経路データを読み込み中...")
    all_stations = list(WALK_MINUTES.keys())
    calculated_routes_dic = load_calculated_routes(data_dir, all_stations)
    print(f"  - 経路データ: {len(calculated_routes_dic)} 駅")

    # 3. オフィスエリアごとのデータセットを生成
    print("\n[3/3] オフィスエリアごとのマスターデータを生成中...")

    dataset_dic = {
        'toranomon': TO_TORANOMON_LIST,
        'tokyo': TO_TOKYO_LIST,
        'otsuka': TO_OTSUKA_LIST
    }

    frontend_master_dic = {}
    for office_name, to_station_list in dataset_dic.items():
        print(f"\n  [{office_name}] 対象駅: {len(to_station_list)} 駅")
        frontend_master = make_frontend_master_for_office(
            office_name,
            to_station_list,
            calculated_routes_dic,
            station_coord_price_df,
            data_dir
        )
        frontend_master_dic[office_name] = frontend_master
        print(f"  [{office_name}] データ行数: {len(frontend_master)} 行")

    print("\n" + "=" * 60)
    print("✓ 全ての処理が完了しました")
    print("=" * 60)

    return frontend_master_dic


if __name__ == "__main__":
    main()
