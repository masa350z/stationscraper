let map;
let markers = [];          // 現在表示中のマーカー参照を保持
let currentMode = "price"; // "price" or "commute_time"

// 地図初期化
document.addEventListener("DOMContentLoaded", () => {
  // 地図生成
  map = L.map("map").setView([35.68, 139.69], 11); // 東京付近を中心
  // タイルレイヤ
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '© OpenStreetMap contributors',
  }).addTo(map);

  // ボタンのイベント設定
  document.getElementById("show-rent-btn").addEventListener("click", () => {
    currentMode = "price";
    fetchAndRender();
  });
  document.getElementById("show-time-btn").addEventListener("click", () => {
    currentMode = "commute_time";
    fetchAndRender();
  });

  document.getElementById("apply-filter-btn").addEventListener("click", () => {
    fetchAndRender();
  });

  // 初回の描画
  fetchAndRender();
});

// APIに問い合わせてデータを取得し、地図に描画
function fetchAndRender() {
  clearMarkers();

  const priceMin = parseFloat(document.getElementById("price-min").value) || 0;
  const priceMax = parseFloat(document.getElementById("price-max").value) || 9999;
  const timeMin = parseInt(document.getElementById("time-min").value) || 0;
  const timeMax = parseInt(document.getElementById("time-max").value) || 9999;

  // API呼び出しURLを組み立て
  const url = `/api/stations?price_min=${priceMin}&price_max=${priceMax}&time_min=${timeMin}&time_max=${timeMax}`;

  fetch(url)
    .then(res => res.json())
    .then(data => {
      if (data.length === 0) {
        console.log("該当データがありません");
        return;
      }

      // 今回は "price" or "commute_time" 列を対象に、実際の最小値・最大値を再度取得
      let values = data.map(st => (currentMode === "price") ? st.price : st.commute_time);
      let minVal = Math.min(...values);
      let maxVal = Math.max(...values);

      data.forEach(st => {
        const lat = st.lat;
        const lng = st.lng;
        if (!lat || !lng) return;

        // 現在モードが家賃なら st.price、通勤時間なら st.commute_time
        let val = (currentMode === "price") ? st.price : st.commute_time;
        let color = getJetColor(val, minVal, maxVal);

        // マーカー（円マーカー）の大きさを2倍 (半径=12)
        let circle = L.circleMarker([lat, lng], {
          radius: 12,
          fillColor: color,
          color: "#000",      // 枠線
          weight: 1,
          opacity: 1,
          fillOpacity: 0.7
        }).addTo(map);

        // ポップアップ（駅情報表示）
        circle.bindPopup(`
          <b>${st.station}</b> (${st.line})<br>
          家賃: ${st.price} 万円<br>
          通勤時間: ${st.commute_time} 分
        `);

        markers.push(circle);
      });
    })
    .catch(err => console.error(err));
}

// 既存マーカーを全消去
function clearMarkers() {
  markers.forEach(m => {
    map.removeLayer(m);
  });
  markers = [];
}

/**
 * Matplotlibのjetカラーマップに近い色を返す
 * value  : 値
 * minVal : データ最小値
 * maxVal : データ最大値
 */
function getJetColor(value, minVal, maxVal) {
  // minVal == maxVal の場合を考慮（全データ同じ値なら固定色）
  if (minVal === maxVal) {
    return "rgb(127,127,127)"; // グレーなど適当
  }

  // 0～1に正規化
  let t = (value - minVal) / (maxVal - minVal);
  if (t < 0) t = 0;
  if (t > 1) t = 1;

  // "jet"風の5点: (0.0 -> #000080), (0.25 -> #0000FF), (0.5 -> #00FFFF), (0.75 -> #FFFF00), (1.0 -> #FF0000)
  // [位置(0～1), R, G, B]
  let stops = [
    [0.0,   0,   0, 128],
    [0.25,  0,   0, 255],
    [0.5,   0, 255, 255],
    [0.75, 255, 255,   0],
    [1.0,  255,   0,   0]
  ];

  // t が所属する区間を見つけ、線形補完
  for (let i = 0; i < stops.length - 1; i++) {
    const [t1, r1, g1, b1] = stops[i];
    const [t2, r2, g2, b2] = stops[i + 1];

    if (t >= t1 && t <= t2) {
      const ratio = (t - t1) / (t2 - t1);
      const r = Math.round(r1 + ratio * (r2 - r1));
      const g = Math.round(g1 + ratio * (g2 - g1));
      const b = Math.round(b1 + ratio * (b2 - b1));
      return `rgb(${r}, ${g}, ${b})`;
    }
  }

  // 万一 t==1.0 超えたとかの場合は最後の色
  const last = stops[stops.length - 1];
  return `rgb(${last[1]}, ${last[2]}, ${last[3]})`;
}
