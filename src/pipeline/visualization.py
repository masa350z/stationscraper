import pandas as pd
import matplotlib.pyplot as plt

def plot_scatter(file_path: str,
                 lat_col: str = 'lat',
                 lng_col: str = 'lng',
                 color_col: str = 'price',
                 lat_min: float = 35.5,
                 lat_max: float = 35.9,
                 lng_min: float = 139.4,
                 lng_max: float = 140.0,
                 cmap_min: float = 0.0,
                 cmap_max: float = 20.0,
                 marker_size: int = 50,
                 alpha: float = 0.75,
                 resolution=(1280, 720),
                 output_file='figure.png'):
    """
    CSVファイルの緯度経度から散布図を作り、色を任意の列で設定する。
    """
    df = pd.read_csv(file_path)
    df = df.dropna(subset=[lat_col, lng_col, color_col])
    df = df[(df[lat_col] >= lat_min) & (df[lat_col] <= lat_max) &
            (df[lng_col] >= lng_min) & (df[lng_col] <= lng_max)]

    fig, ax = plt.subplots(figsize=(resolution[0]/100, resolution[1]/100))
    sc = ax.scatter(df[lng_col], df[lat_col],
                    c=df[color_col],
                    cmap='jet',
                    vmin=cmap_min,
                    vmax=cmap_max,
                    s=marker_size,
                    alpha=alpha,
                    edgecolors='none')
    plt.colorbar(sc, label=color_col)

    x_range = lng_max - lng_min
    y_range = lat_max - lat_min
    ax.set_aspect(abs(x_range/y_range), adjustable='box')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title(f'Scatter of {color_col}')

    plt.savefig(output_file, dpi=100, transparent=True)
    print(f"プロット完了: {output_file}")
    plt.close()