# %%
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


def plot_data2(price_file_path, min_file_path, output_filename,
               lat_min, lat_max, lng_min, lng_max,
               resolution,
               marker_size, maker_alpha,
               price_min, price_max,
               min_min, min_max):

    params = [[price_min, price_max],
              [min_min, min_max]]

    # プロットの作成
    fig, ax = plt.subplots(
        figsize=(resolution[0] / 100, resolution[1] / 100))

    for i, path in enumerate([price_file_path, min_file_path]):
        mode = 'price' if i == 0 else 'min'
        # データの読み込み
        data = pd.read_csv(path)

        # フィルタリング
        filtered_data = data[(data['lat'] >= lat_min) & (data['lat'] <= lat_max) &
                             (data['lng'] >= lng_min) & (data['lng'] <= lng_max) &
                             (data[mode] >= params[i][0]) & (data[mode] <= params[i][1])]

        y_ = filtered_data['lat']
        if i == 0:
            mapcolor = 'YlOrRd'
            x_ = filtered_data['lng'] + 0.003

        else:
            mapcolor = 'YlGnBu'
            x_ = filtered_data['lng'] - 0.003

        sc = ax.scatter(x_, y_,
                        c=filtered_data[mode], cmap=mapcolor, marker='s', s=marker_size, alpha=maker_alpha,
                        # edgecolors='none'
                        )
        # plt.colorbar(sc, label=mode)
        # sc.set_clim(colormap_min, colormap_max)

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


# %%
# mode = 'min'
mode = 'price'

# file_path = 'csv/to_roppongi/all_{}_code.csv'.format(mode)  # CSVファイルのパス
file_path = 'csv/to_shibuya/trans_min_price_2ldk_filtered_code.csv'
# 保存する画像のファイル名
output_filename = 'csv/to_shibuya/{}_visualization.png'.format(mode)
mx_ = 20
mn_ = 0

plot_data(file_path, 35.5, 35.9, 139.4, 140,
          220*5, (3840*2, 2160*2), mn_, mx_, 0.75, output_filename,
          mode, mn_, mx_)
# %%
mode = 'min'

# 保存する画像のファイル名
output_filename = 'csv/to_shibuya/{}_visualization.png'.format(mode)
mx_ = 60
mn_ = 0

plot_data(file_path, 35.5, 35.9, 139.4, 140,
          220*5, (3840*2, 2160*2), mn_, mx_, 0.75, output_filename,
          mode, mn_, mx_)
# %%
price_file_path = 'csv/to_roppongi/all_price_code.csv'
min_file_path = 'csv/to_roppongi/all_min_code.csv'
output_filename = 'csv/to_roppongi/visualization.png'

plot_data2(price_file_path, min_file_path, output_filename,
           35.5, 35.9, 139.4, 140,
           (3840*2, 2160*2),
           220*2, 0.75,
           3, 7,
           30, 60)

# %%
