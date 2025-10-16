# %%
"""
座標が欠損している426駅の座標をGoogle Maps APIで取得するスクリプト
"""
import pandas as pd
import sys
import time

# src/のモジュールをインポート
sys.path.insert(0, 'src')
from apis.google_maps import geocode_location

# 1. 座標が欠損している426駅を抽出
df = pd.read_csv('data/station_address_with_coordinates.csv')
missing_coords = df[df['lat'].isna()].copy()

print(f"座標欠損駅数: {len(missing_coords)}駅")
print(f"\n座標取得を開始します...\n")

# 2. 座標取得結果を格納するリスト
results = []
# %%
count = 0
# %%
# 3. 各駅の座標を取得
for idx, row in missing_coords.iterrows():
    line = row['line']
    station = row['station']

    # 複数の検索クエリパターンを試行
    query_patterns = [
        f"{line} {station}駅",      # パターン1: "XX線 XX駅"
        f"{line} {station}",         # パターン2: "XX線 XX" (駅を外す)
        f"{station}駅",              # パターン3: "XX駅" (路線名を外す)
        f"{station}",                # パターン4: "XX" (駅も路線名も外す)
    ]

    lat, lng = None, None
    used_query = None

    # 各パターンを順番に試行
    for query in query_patterns:
        lat, lng = geocode_location(query)
        if lat is not None and lng is not None:
            used_query = query
            break  # 成功したらループを抜ける
        time.sleep(0.5)  # 失敗時も少し待機

    # 結果を記録
    result = {
        'line': line,
        'station': station,
        'query': used_query if used_query else query_patterns[0],
        'lat': lat,
        'lng': lng,
        'success': lat is not None and lng is not None
    }
    results.append(result)

    # 進捗表示
    if (len(results)) % 10 == 0:
        success_count = sum(1 for r in results if r['success'])
        print(f"進捗: {len(results)}/{len(missing_coords)} "
              f"(成功: {success_count}, 失敗: {len(results) - success_count})")

    # API制限対策: 1秒待機
    time.sleep(1)
    count += 1
    # if count >= 10:
    #     break

# 4. 結果をDataFrameに変換
df_results = pd.DataFrame(results)

# 5. 統計情報を表示
success_count = df_results['success'].sum()
failed_count = len(df_results) - success_count

print(f"\n=== 座標取得完了 ===")
print(f"総数: {len(df_results)}駅")
print(f"成功: {success_count}駅 ({success_count/len(df_results)*100:.1f}%)")
print(f"失敗: {failed_count}駅 ({failed_count/len(df_results)*100:.1f}%)")

# 6. 結果をCSVに保存
output_path = 'data/missing_coords_geocoded.csv'
df_results.to_csv(output_path, index=False)
print(f"\n結果を保存: {output_path}")

# 7. 失敗した駅のリストを表示
if failed_count > 0:
    print(f"\n座標取得に失敗した駅（最初の10件）:")
    failed_stations = df_results[~df_results['success']].head(10)
    for _, row in failed_stations.iterrows():
        print(f"  {row['line']}, {row['station']} (クエリ: {row['query']})")

# %%
