import matplotlib.pyplot as plt
import pandas as pd


def plot_data(file_path, lat_min, lat_max, lng_min, lng_max, marker_size,
              resolution, cmap_min, cmap_max,
              alpha, output_filename,
              mode, mode_min, mode_max):
    # データの読み込み
    data = pd.read_csv(file_path)

    # フィルタリング
    filtered_data = data[(data['lat'] >= lat_min) & (data['lat'] <= lat_max) &
                         (data['lng'] >= lng_min) & (data['lng'] <= lng_max) &
                         (data[mode] >= mode_min) & (data[mode] <= mode_max)]

    # プロットの作成
    fig, ax = plt.subplots(figsize=(resolution[0] / 100, resolution[1] / 100))
    sc = ax.scatter(filtered_data['lng'], filtered_data['lat'],
                    c=filtered_data[mode], cmap='jet', marker='o', s=marker_size, alpha=alpha,
                    edgecolors='none')
    plt.colorbar(sc, label=mode)
    sc.set_clim(cmap_min, cmap_max)

    # アスペクト比の調整
    x_range = lng_max - lng_min
    y_range = lat_max - lat_min
    ax.set_aspect(abs(x_range/y_range), adjustable='box')

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Price Visualization with Equal Scale and Transparency')

    # 透明な背景で画像として保存
    plt.savefig(output_filename, dpi=100, transparent=True)
    plt.show()


mode = 'min'
# mode = 'price'

file_path = 'csv/to_roppongi/all_{}_code.csv'.format(mode)  # CSVファイルのパス
# 保存する画像のファイル名
output_filename = 'csv/to_roppongi/{}_visualization.png'.format(mode)
mx_ = 60
mn_ = 30

plot_data(file_path, 35.3, 36, 139.3, 140,
          200, (3840, 2160), mn_, mx_, 0.75, output_filename,
          mode, 30, 60)
