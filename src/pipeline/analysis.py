import pandas as pd
from config import MAX_TRANS_DEFAULT, MAX_TIME_DEFAULT, MAX_PRICE_DEFAULT

def evaluate_and_split(input_csv: str, output_dir: str) -> None:
    """
    乗り換え回数・所要時間・家賃などを判定して
    条件を満たす行を集め、さらに所要時間帯で分割してCSV保存する例。
    """
    df = pd.read_csv(input_csv)

    c1 = df['trans'] <= MAX_TRANS_DEFAULT
    c2 = df['price'] <= MAX_PRICE_DEFAULT
    c3 = df['train+walk_min'] <= MAX_TIME_DEFAULT

    ndf = df[c1 & c2 & c3].reset_index(drop=True)
    out_path = f"{output_dir}/all.csv"
    ndf.to_csv(out_path, index=False)
    print(f"全体絞り込みを保存: {out_path}")

    for i in range(6):
        lower = i*10
        upper = (i+1)*10
        tmp = ndf[(ndf['train+walk_min'] > lower) & (ndf['train+walk_min'] <= upper)].reset_index(drop=True)
        split_path = f"{output_dir}/{lower}_{upper}.csv"
        tmp.to_csv(split_path, index=False)
        print(f"{split_path} に保存しました。")