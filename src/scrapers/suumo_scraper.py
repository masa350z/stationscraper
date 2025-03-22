import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

from tqdm import tqdm
from src.config import SCRAPING_SLEEP_SEC, SCRAPING_RETRY_COUNT


def scrape_suumo_rent(pref_list, output_csv_path, room_type='one_room'):
    """
    SUUMOの沿線×駅の家賃相場情報をスクレイピングしてCSVに保存する。
    pref_list: ['tokyo', 'kanagawa', 'saitama', 'chiba'] のような都道府県URL識別子リスト
    output_csv_path: 保存先CSVファイル
    """
    room_type_index = {'one_room': '01',
                       '1k': '02',
                       '1dk': '02',
                       '1ldk': '03',
                       '2k': '03',
                       '2dk': '03',
                       '2ldk': '04',
                       '3k': '04',
                       '3dk': '04',
                       '3ldk': '05',
                       '4k': '05'}

    # 辞書に無いroom_typeが指定された場合はエラーを出す
    if room_type not in room_type_index:
        valid_keys = ", ".join(room_type_index.keys())
        raise ValueError(f"Unsupported room_type: '{room_type}'. Valid options: {valid_keys}")

    base_url = 'https://suumo.jp/chintai/soba/{}/ensen/'

    result = []
    for pref in pref_list:
        url = base_url.format(pref)
        soup = _safe_get_soup(url)
        master_table = soup.find('table', class_='searchtable')
        if not master_table:
            print(f"想定外の構造です: {url}")
            continue

        lines = master_table.find_all('a')
        for line in tqdm(lines):
            line_name = line.text.strip()
            line_href = line.get('href', '')
            if not line_href:
                continue

            full_url = 'https://suumo.jp' + line_href + '?mdKbn=' + room_type_index[room_type]
            line_soup = _safe_get_soup(full_url)
            table = line_soup.find('table', class_='graphpanel_matrix')
            if not table:
                continue

            stations = table.find_all('tr', class_='js-graph-data')
            for st in stations:
                tds = st.find_all('td')
                if len(tds) < 2:
                    continue
                station_name = tds[0].text.strip()
                price_str = tds[1].text.strip().replace('万円', '')
                try:
                    price = float(price_str)
                    result.append([line_name, station_name, price])
                except ValueError:
                    pass
            time.sleep(SCRAPING_SLEEP_SEC)

    df = pd.DataFrame(result, columns=['line', 'station', 'price'])
    df.drop_duplicates(inplace=True)
    df.to_csv(output_csv_path, index=False)
    print(f"SUUMOスクレイピング完了: {output_csv_path}")


def _safe_get_soup(url: str):
    """
    requests + BeautifulSoupを安全に実行する簡易ユーティリティ
    """
    for _ in range(SCRAPING_RETRY_COUNT):
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                return BeautifulSoup(res.text, "html.parser")
        except Exception as e:
            print(f"リクエストに失敗: {e}")
        time.sleep(SCRAPING_SLEEP_SEC)
    raise RuntimeError(f"リトライ上限に達しました: {url}")