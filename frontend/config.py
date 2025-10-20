"""
frontend - 設定ファイル

filtered_master_toranomon_common_2k.csv を単一のマスターデータとして使用する
完全独立型のシンプルなWebアプリケーション設定
"""
import os

# CSVデータファイルのパス
CSV_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "frontend_master",
    "filtered",
    "filtered_master_toranomon_common_2k.csv"
)

# フィルタリングのデフォルト値
DEFAULT_MAX_PRICE = 12.0  # 最大家賃（万円）
DEFAULT_MAX_TIME = 60     # 最大所要時間（分、電車+徒歩）
DEFAULT_MAX_TRANS = 2     # 最大乗り換え回数

# サーバー設定
HOST = '0.0.0.0'
PORT = 5002  # nxt_genの5001と被らないように5002を使用
DEBUG = True

# 地図の初期表示位置（東京駅周辺）
MAP_CENTER_LAT = 35.6812
MAP_CENTER_LNG = 139.7671
MAP_ZOOM = 11
