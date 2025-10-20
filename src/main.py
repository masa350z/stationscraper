# %%
"""
データパイプラインのメイン実行スクリプト

駅データ、家賃データ、経路情報を取得・統合するパイプラインを実行する。
各処理の詳細はfunctions.pyに定義されている。
"""
import os
from functions import (
    make_station_master,
    add_geocode_to_station_master,
    make_rent_data,
    make_merged_data,
    get_or_calculate_route,
)
from config import ROOM_TYPE, WALK_MINUTES

# %%
# データパイプラインのメイン処理
# 各関数は入力としてDataFrameを受け取り、処理結果のDataFrameを返す

data_dir = "../data"

# 1. 駅マスタを取得
station_master_df = make_station_master()

# 2. 座標を付与
station_with_coords_df = add_geocode_to_station_master(
    station_master_df,
    os.path.join(data_dir, "station_master", "station_address_with_coordinates.csv")
)
station_with_coords_df.to_csv(
    os.path.join(data_dir, "station_master", "station_address_with_coordinates.csv"),
    index=False
)

# 3. 家賃データを取得
rent_data_df = make_rent_data()

# 4. マージ
station_coord_price_df = make_merged_data(station_with_coords_df, rent_data_df)
station_coord_price_df.to_csv(
    os.path.join(data_dir, "station_coord_price", f"station_coord_price_{ROOM_TYPE}.csv"),
    index=False
)

# 5. 各目的地駅への経路計算（既存ファイルがあればキャッシュから読み込み）
for to_station in list(WALK_MINUTES.keys()):
    output_path = os.path.join(
        data_dir, "calclated_routes", f"calclated_routes_{to_station}.csv"
    )
    df = get_or_calculate_route(station_coord_price_df, to_station, output_path)
    df.to_csv(output_path, index=False)
