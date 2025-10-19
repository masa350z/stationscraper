"""
nxt_gen プロジェクトの設定ファイル
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
EKISPERT_KEY = os.environ.get("EKISPERT_KEY")

# 既存データファイルのパス（プロジェクトルートからの相対パス）
STATION_MASTER_PATH = "../data/station_master/station_address_with_coordinates.csv"
PRICE_ORIGINAL_PATH = "../data/price_by_station/price_by_station_one_room.csv"

# 対象駅と駅からの徒歩時間（分）
TARGET_STATIONS = {
    '虎ノ門ヒルズ': 4,
    '虎ノ門': 4,
    '新橋': 20,
    '霞ケ関': 13,
    '国会議事堂前': 10,
    '溜池山王': 10,
    '桜田門': 16,
    '内幸町': 13,
}

# Ekispert API設定
API_SLEEP_SEC = 1  # API呼び出し間のスリープ時間
API_BATCH_SIZE = 50  # 一度に処理する駅数
SAVE_INTERVAL = 250  # 中間保存する駅数間隔

# フィルタリング条件のデフォルト値
MAX_PRICE_DEFAULT = 10.0  # 万円
MAX_TIME_DEFAULT = 60  # 分（電車時間＋徒歩時間）
MAX_TRANS_DEFAULT = 2  # 回（乗り換え回数）

# 出力ファイル設定
OUTPUT_DIR = "data"
FINAL_CSV_NAME = "stations_complete.csv"