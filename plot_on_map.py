import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pandas as pd


def plot_data_on_map(file_path, lat_min, lat_max, lng_min, lng_max, marker_size, alpha, output_filename):
    # データの読み込み
    data = pd.read_csv(file_path)

    # フィルタリング
    filtered_data = data[(data['lat'] >= lat_min) & (data['lat'] <= lat_max) &
                         (data['lng'] >= lng_min) & (data['lng'] <= lng_max)]

    # マップの作成
    plt.figure(figsize=(12, 8))
    m = Basemap(projection='merc', llcrnrlat=lat_min, urcrnrlat=lat_max,
                llcrnrlon=lng_min, urcrnrlon=lng_max, resolution='i')
    m.drawcoastlines()
    m.drawcountries()
    m.fillcontinents(color='lightgray', lake_color='aqua')
    m.drawmapboundary(fill_color='aqua')

    # ポイントのプロット
    x, y = m(filtered_data['lng'].values, filtered_data['lat'].values)
    m.scatter(x, y, s=marker_size,
              c=filtered_data['price'], cmap='jet', alpha=alpha, edgecolors='none')

    # 画像として保存
    plt.savefig(output_filename, dpi=300, transparent=True)
    plt.show()
