import requests
from config import GOOGLE_MAPS_KEY


def geocode_location(location_name: str) -> tuple:
    """
    指定した地名(駅名など)の緯度経度を取得する。
    戻り値: (lat, lng) or (None, None)
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location_name,
        "key": GOOGLE_MAPS_KEY
    }
    res = requests.get(url, params=params)
    if res.status_code != 200:
        return (None, None)

    data = res.json().get("results", [])
    if not data:
        return (None, None)
    loc = data[0]["geometry"]["location"]
    return (loc["lat"], loc["lng"])