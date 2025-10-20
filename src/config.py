import os
from dotenv import load_dotenv

load_dotenv()

EKISPERT_KEY = os.environ.get("EKISPERT_KEY")
GOOGLE_MAPS_KEY = os.environ.get("GOOGLE_MAPS_KEY")

# スリープ時間やスクレイピング時のリトライ回数など
SCRAPING_SLEEP_SEC = 10
SCRAPING_RETRY_COUNT = 3

ROOM_TYPE = '2k'

# プロジェクト内で使う定数例（拡張しやすいようにまとめる）
WALK_MINUTES = {
    '虎ノ門ヒルズ': 4,
    '虎ノ門': 4,
    '新橋': 20,
    '霞ケ関': 13,
    '国会議事堂前': 10,
    '溜池山王': 10,
    '桜田門': 16,
    '内幸町': 13,
    '大塚': 8,
    '東京': 2,
    '日本橋': 8,
    '大手町': 9,
    '京橋': 6,
    '銀座一丁目': 8,
    '宝町': 10,
    '八丁堀': 15,
}

# 通勤先の駅一覧。フロントエンドで表示されるもの。
TO_TORANOMON_LIST = ['虎ノ門ヒルズ',
                     '虎ノ門',
                     '新橋',
                     '霞ケ関',
                     '国会議事堂前',
                     '溜池山王',
                     '桜田門',
                     '内幸町']

TO_TOKYO_LIST = ['東京',
                 '日本橋',
                 '大手町',
                 '京橋',
                 '銀座一丁目',
                 '宝町',
                 '八丁堀']

TO_OTSUKA_LIST = ['大塚']
