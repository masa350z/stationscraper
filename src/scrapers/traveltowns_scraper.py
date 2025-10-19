import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

from tqdm import tqdm
from config import SCRAPING_SLEEP_SEC, SCRAPING_RETRY_COUNT


def scrape_traveltowns_kanto(output_csv_path: str) -> None:
    """
    関東の鉄道路線URLと路線名を取得し、さらに各路線ページから駅一覧をスクレイピングしてCSVに保存する。
    output_csv_path: 最終的に駅名を保存するCSVのパス
    """
    base_url = 'https://www.traveltowns.jp/railwaylines/kanto/'
    res = _safe_get(base_url)
    soup = BeautifulSoup(res.text, "html.parser")

    tables = soup.find_all('table')
    if len(tables) < 5:
        print("想定外のHTML構造です。テーブルが不足しています。")
        return

    # それぞれのテーブルから路線のリンクを取得（JR、私鉄、地下鉄、ローカルなど）
    jr_west_table = tables[1]
    shitetsu_table = tables[2]
    subway_table = tables[3]
    local_table = tables[4]

    # リンク抽出
    jr_links = jr_west_table.find_all('a')
    shitetsu_links = shitetsu_table.find_all('a')
    subway_links = subway_table.find_all('a')
    local_links = local_table.find_all('a')

    # 路線ページ一覧を作る
    line_info = []
    for link in jr_links + shitetsu_links + subway_links + local_links:
        line_url = 'https://www.traveltowns.jp' + link.get('href', '')
        line_name = link.text.strip()
        line_info.append((line_url, line_name))

    # 各路線ページにアクセスして駅名を取得
    station_data = []
    for (line_url, line_name) in tqdm(line_info):
        try:
            line_page = _safe_get(line_url)
            lsoup = BeautifulSoup(line_page.text, "html.parser")
            line_table = lsoup.find('table')
            if not line_table:
                continue

            trs = line_table.find_all('tr')[1:]
            for tr in trs:
                a_tag = tr.find('a')
                if a_tag:
                    station_name = a_tag.text.strip()
                    station_data.append([line_name, station_name])
        except Exception as e:
            print(f"エラーが発生しました: {e}")
        time.sleep(SCRAPING_SLEEP_SEC)

    df = pd.DataFrame(station_data, columns=['line', 'station'])
    df.drop_duplicates(inplace=True)
    df.to_csv(output_csv_path, index=False)
    print(f"スクレイピングが完了しました: {output_csv_path}")


def _safe_get(url: str):
    """
    requests.getを安全に行い、必要ならリトライを実行する簡易ユーティリティ
    """
    for _ in range(SCRAPING_RETRY_COUNT):
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                return res
        except Exception as e:
            print(f"リクエストに失敗しました: {e}")
        time.sleep(SCRAPING_SLEEP_SEC)
    raise RuntimeError(f"リトライ上限に達しました: {url}")
