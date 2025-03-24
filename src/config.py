import os
from dotenv import load_dotenv

load_dotenv()

EKISPERT_KEY = os.environ.get("EKISPERT_KEY")
GOOGLE_MAPS_KEY = os.environ.get("GOOGLE_MAPS_KEY")

# スリープ時間やスクレイピング時のリトライ回数など
SCRAPING_SLEEP_SEC = 10
SCRAPING_RETRY_COUNT = 3

ROOM_TYPE = 'one_room'

# プロジェクト内で使う定数例（拡張しやすいようにまとめる）
# WALK_MINUTES = {
#     '虎ノ門ヒルズ': 4,
#     '虎ノ門': 4,
#     '新橋': 20,
#     '霞ケ関': 13,
#     '国会議事堂前': 10,
#     '溜池山王': 10,
#     '桜田門': 16,
#     '内幸町': 13,
# }

WALK_MINUTES = {
    '大塚': 8,
}
