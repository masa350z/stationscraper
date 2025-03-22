import os
from dotenv import load_dotenv

load_dotenv()

EKISPERT_KEY = os.environ.get("EKISPERT_KEY")
GOOGLE_MAPS_KEY = os.environ.get("GOOGLE_MAPS_KEY")

# 必要なパラメータ類をまとめる
MAX_TRANS_DEFAULT = 100
MAX_TIME_DEFAULT = 60
MAX_PRICE_DEFAULT = 65

# スリープ時間やスクレイピング時のリトライ回数など
SCRAPING_SLEEP_SEC = 10
SCRAPING_RETRY_COUNT = 3

ROOM_TYPE = '2k'

# プロジェクト内で使う定数例（拡張しやすいようにまとめる）
WALK_MINUTES = {
    '六本木': 7,
    '六本木一丁目': 17,
    '乃木坂': 7,
    '赤坂': 14
}