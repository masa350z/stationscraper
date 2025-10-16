"""
nxt_gen メインパイプライン
既存の座標付き駅マスタと家賃データを使用して、
経路情報を追加した完全なデータセットを作成
"""
import os
import sys
import pandas as pd
from config import TARGET_STATIONS, FINAL_CSV_NAME, MAX_PRICE_DEFAULT, MAX_TIME_DEFAULT, MAX_TRANS_DEFAULT, API_BATCH_SIZE, SAVE_INTERVAL
from data_loader import load_station_master, load_price_data, load_existing_route_data, save_data, save_route_data_to_legacy_format, save_intermediate_route_data, load_fallback_route_data
from route_collector import collect_route_info
from data_processor import prepare_final_dataset, filter_stations, merge_station_and_price

def process_route_data(df_station, df_price, target_station, walk_minutes):
    """
    既存データの確認と不足分の追加収集を行う

    Parameters:
    -----------
    df_station : pandas.DataFrame
        駅マスタデータ
    df_price : pandas.DataFrame
        家賃データ
    target_station : str
        対象駅名
    walk_minutes : int
        徒歩時間（分）

    Returns:
    --------
    pandas.DataFrame : 統合された経路データ
    """
    # 既存データを読み込み
    df_route_existing = load_existing_route_data(target_station)

    # 経路情報が必要な駅を特定（家賃データとマージ可能な駅）
    df_merged = merge_station_and_price(df_station, df_price)

    # 既存データでカバーされている駅を確認
    if df_route_existing is not None:
        existing_stations = set(zip(df_route_existing['line'], df_route_existing['station']))
        print(f"  既存データ: {len(existing_stations)}駅")
    else:
        existing_stations = set()
        print(f"  既存データなし")

    # 必要な全駅を特定
    all_stations = set(zip(df_merged['line'], df_merged['station']))
    missing_stations = all_stations - existing_stations

    if missing_stations:
        print(f"  追加収集が必要: {len(missing_stations)}駅")

        # フォールバックデータを読み込み
        print("  フォールバックデータ（六本木への経路）を使用します")
        fallback_data = load_fallback_route_data()

        # 不足分の駅データを準備
        df_to_collect = df_merged[
            df_merged[['line', 'station']].apply(tuple, axis=1).isin(missing_stations)
        ]

        # フォールバックデータから経路情報を作成
        records = []
        filled_count = 0
        not_found_count = 0

        for _, row in df_to_collect.iterrows():
            station = row['station']
            line = row['line']
            price = row.get('price', None)  # 元データから家賃情報を取得

            # フォールバックデータから取得
            if station in fallback_data:
                estimated_min, fallback_price = fallback_data[station]
                # 元データに家賃がない場合はフォールバックデータから使用
                if price is None or pd.isna(price):
                    price = fallback_price

                # 乗換回数は推定（15分未満:0回, 15-30分:1回, それ以上:2回）
                if estimated_min < 15:
                    trans = 0
                elif estimated_min < 30:
                    trans = 1
                else:
                    trans = 2

                record = {
                    'line': line,
                    'station': station,
                    'price': price,  # 家賃情報を追加
                    'to_station': target_station,
                    'trans': trans,
                    'train_min': estimated_min,
                    'walk_min': walk_minutes,
                    'total_min': estimated_min + walk_minutes
                }
                records.append(record)
                filled_count += 1
            else:
                not_found_count += 1

        print(f"  フォールバックデータで補完: {filled_count}駅")
        if not_found_count > 0:
            print(f"  データなし: {not_found_count}駅")

        df_route_new = pd.DataFrame(records)

        # 既存データと統合
        if df_route_existing is not None:
            df_route = pd.concat([df_route_existing, df_route_new], ignore_index=True)
        else:
            df_route = df_route_new

        # 最終データを保存
        save_route_data_to_legacy_format(df_route, target_station)
        print(f"  収集完了: 合計{len(df_route)}駅の経路情報")
    else:
        print(f"  追加収集不要（全駅カバー済み）")
        df_route = df_route_existing

    return df_route

def main():
    """
    メインパイプライン実行
    """
    print("=" * 60)
    print("nxt_gen データパイプライン開始")
    print("=" * 60)

    # 1. 既存データの読み込み
    print("\n[1] 既存データマスタを読み込み中...")
    df_station = load_station_master()
    df_price = load_price_data()

    # 2. 経路情報の収集（既存データと新規収集を統合）
    print("\n[2] 経路情報を収集中...")
    route_data_dict = {}

    for target_station, walk_minutes in TARGET_STATIONS.items():
        df_route = process_route_data(
            df_station, df_price, target_station, walk_minutes
        )
        route_data_dict[target_station] = df_route

    # 3. データの統合と処理
    print("\n[3] データを統合・処理中...")
    df_final = prepare_final_dataset(df_station, df_price, route_data_dict)

    # 4. フィルタリング（オプション）
    print(f"\n[4] データをフィルタリング中...")
    print(f"  条件: 家賃 <= {MAX_PRICE_DEFAULT}万円, 所要時間 <= {MAX_TIME_DEFAULT}分, 乗換 <= {MAX_TRANS_DEFAULT}回")
    df_filtered = filter_stations(
        df_final,
        max_price=MAX_PRICE_DEFAULT,
        max_time=MAX_TIME_DEFAULT,
        max_trans=MAX_TRANS_DEFAULT
    )
    print(f"  フィルタ後: {len(df_filtered)}駅")

    # 5. 結果を保存
    print(f"\n[5] 結果を保存中...")
    save_data(df_final, FINAL_CSV_NAME)
    save_data(df_filtered, f"filtered_{FINAL_CSV_NAME}")

    print("\n" + "=" * 60)
    print("パイプライン完了!")
    print("=" * 60)
    print(f"\n出力ファイル:")
    print(f"  - data/{FINAL_CSV_NAME} (全データ: {len(df_final)}駅)")
    print(f"  - data/filtered_{FINAL_CSV_NAME} (フィルタ済: {len(df_filtered)}駅)")

    # 6. サンプルデータを表示
    if not df_filtered.empty:
        print("\nサンプルデータ（家賃が安い上位5駅）:")
        sample = df_filtered.nsmallest(5, 'price', keep='first')[
            ['station', 'line', 'price', 'total_min'] if 'total_min' in df_filtered.columns
            else ['station', 'line', 'price']
        ]
        print(sample.to_string(index=False))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n処理が中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)