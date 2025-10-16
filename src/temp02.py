# %%
import pandas as pd
import os

from scrapers.traveltowns_scraper import scrape_traveltowns_kanto
from scrapers.suumo_scraper import scrape_suumo_rent

from apis.ekispert import get_minimum_route_info_between_stations
from apis.google_maps import geocode_location

from pipeline.data_cleaning import merge_station_info, add_walking_time

from config import ROOM_TYPE
# %%

data_dir = "../data"
station_address_csv = os.path.join(data_dir, "station_address.csv")
if not os.path.exists(station_address_csv):
    print("[1] Traveltownsから駅マスタを取得...")
    scrape_traveltowns_kanto(station_address_csv)
else:
    print("[1] 駅マスタCSVが既に存在します:", station_address_csv)

# 2. スクレイピング（SUUMO家賃）
station_price_csv = os.path.join(
    data_dir, "station_price", f"station_price_{ROOM_TYPE}.csv")
if not os.path.exists(station_price_csv):
    print(f"[2] SUUMOから家賃相場({ROOM_TYPE})を取得...")
    pref_list = ['tokyo', 'kanagawa', 'saitama', 'chiba']
    scrape_suumo_rent(pref_list, station_price_csv, room_type=ROOM_TYPE)
else:
    print("[2] 家賃相場CSVが既に存在します:", station_price_csv)

# 3. 駅マスタと家賃CSVを結合
merged_csv = os.path.join(
    data_dir, "output", "price_info", f"price_by_station_{ROOM_TYPE}.csv")
if not os.path.exists(merged_csv):
    print("[3] 駅マスタと家賃をマージ...")
    merge_station_info(station_address_csv, station_price_csv, merged_csv)
else:
    print(f"[3] price_by_station_{ROOM_TYPE}.csv が既に存在:", merged_csv)

# %%
# 全駅データを読み込み（2496駅）
station_address = pd.read_csv('../data/station_address.csv')
print(f"全駅データ: {len(station_address)}駅")
station_address.head()

# %%
# 緯度経度データを読み込み（1111駅分）
stations_lat_lng = pd.read_csv('../mapapp/stations.csv')
print(f"緯度経度データ: {len(stations_lat_lng)}駅")

# 必要なカラムのみ抽出
stations_lat_lng = stations_lat_lng[['line', 'station', 'lat', 'lng']]

# 重複を除去（同じline+stationの組み合わせ）
stations_lat_lng = stations_lat_lng.drop_duplicates(subset=['line', 'station']).reset_index(drop=True)
print(f"重複除去後: {len(stations_lat_lng)}駅")
stations_lat_lng.head()

# %%
# 左外部結合で全駅データに緯度経度を追加（緯度経度がない駅はNaNになる）
merged_df = pd.merge(
    station_address,
    stations_lat_lng,
    on=['line', 'station'],
    how='left'
)

print(f"結合後のデータ: {len(merged_df)}駅")
print(f"緯度経度あり: {merged_df['lat'].notna().sum()}駅")
print(f"緯度経度なし: {merged_df['lat'].isna().sum()}駅")

# データの確認
merged_df.head(10)

# %%
# all_min_code.csv と all_price_code.csv から座標データを補完
print("\n座標データの補完処理を開始...")

# 追加の座標データソースを読み込み
min_coords = pd.read_csv('../all_min_code.csv')
price_coords = pd.read_csv('../all_price_code.csv')

# 両ファイルから座標データを統合（fromカラムが駅名）
# 重複を除去し、最初に見つかった座標を採用
additional_coords = pd.concat([
    min_coords[['from', 'lat', 'lng']].rename(columns={'from': 'station'}),
    price_coords[['from', 'lat', 'lng']].rename(columns={'from': 'station'})
]).drop_duplicates(subset=['station'], keep='first').reset_index(drop=True)

print(f"追加座標データ: {len(additional_coords)}駅分")

# 座標が欠損している駅すべてに対して補完処理
missing_coords_mask = merged_df['lat'].isna()
print(f"座標欠損駅数: {missing_coords_mask.sum()}駅")

# 補完処理（同じ駅名には同じ座標を入れる）
filled_count = 0
filled_stations = set()

for idx in merged_df[missing_coords_mask].index:
    station_name = merged_df.loc[idx, 'station']

    # additional_coordsから座標を検索
    coord_match = additional_coords[additional_coords['station'] == station_name]

    if not coord_match.empty:
        merged_df.loc[idx, 'lat'] = coord_match.iloc[0]['lat']
        merged_df.loc[idx, 'lng'] = coord_match.iloc[0]['lng']
        filled_count += 1
        filled_stations.add(station_name)

print(f"座標補完完了: {filled_count}駅")
print(f"補完した駅名数: {len(filled_stations)}種類")

# 補完後も座標が欠損している駅のリストを作成
still_missing = merged_df[merged_df['lat'].isna()][['line', 'station']].copy()

if len(still_missing) > 0:
    # 駅名ごとにグループ化
    missing_summary = still_missing.groupby('station').agg({
        'line': lambda x: list(x)
    }).reset_index()
    missing_summary.columns = ['station', 'lines']
    missing_summary['num_lines'] = missing_summary['lines'].apply(len)

    print(f"\n補完後も座標が欠損: {len(missing_summary)}駅名")
    print("欠損駅名の例（上位10件）:")
    for _, row in missing_summary.head(10).iterrows():
        lines_str = ', '.join(row['lines'][:3])
        if row['num_lines'] > 3:
            lines_str += f" ... 他{row['num_lines']-3}路線"
        print(f"  {row['station']}: {lines_str}")

    # 欠損駅リストをCSVに保存
    missing_output_path = '../data/stations_still_missing_coords.csv'
    missing_summary.to_csv(missing_output_path, index=False)
    print(f"\n欠損駅リスト保存: {missing_output_path}")

# 最終的な座標補完状況
print(f"\n最終結果:")
print(f"  全駅数: {len(merged_df)}駅")
print(f"  座標あり: {merged_df['lat'].notna().sum()}駅 ({merged_df['lat'].notna().sum()/len(merged_df)*100:.1f}%)")
print(f"  座標なし: {merged_df['lat'].isna().sum()}駅 ({merged_df['lat'].isna().sum()/len(merged_df)*100:.1f}%)")

# %%
# 結合したデータをCSVに保存
output_path = '../data/station_address_with_coordinates.csv'
merged_df.to_csv(output_path, index=False)
print(f"保存完了: {output_path}")

# %%
