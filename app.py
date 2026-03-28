import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import base64
from PIL import Image
import io

geolocator = Nominatim(user_agent="memory_app")

# =====================
# データ保存（簡易）
# =====================
if "memories" not in st.session_state:
    st.session_state.memories = []

# =====================
# タイトル
# =====================
st.title("📍 ゆらの思い出アプリ")

# =====================
# 入力
# =====================
place = st.text_input("場所")
food = st.text_input("食べたもの")
score = st.slider("満足度", 1, 5, 3)
memo = st.text_input("感想")
image = st.file_uploader("写真", type=["png", "jpg", "jpeg"])

# =====================
# 地名→座標
# =====================
def get_lat_lon(place_name):
    try:
        loc = geolocator.geocode(place_name + ", Japan")
        if loc:
            return loc.latitude, loc.longitude
    except:
        pass
    return None, None

# =====================
# 保存
# =====================
if st.button("保存"):
    lat, lon = get_lat_lon(place)

    img_bytes = None
    if image:
        img_bytes = image.read()

    st.session_state.memories.append({
        "place": place,
        "food": food,
        "score": score,
        "memo": memo,
        "lat": lat,
        "lon": lon,
        "image": img_bytes
    })

    st.success("保存したよ！")

# =====================
# 一覧
# =====================
st.subheader("📚 思い出一覧")

for m in st.session_state.memories[-20:]:
    st.write(f"📍 {m['place']}　🍽 {m['food']}　⭐ {m['score']}")
    st.write(f"📝 {m['memo']}")

    if m["image"]:
        st.image(m["image"], width=200)

# =====================
# 地図
# =====================
import base64
import folium
from streamlit_folium import st_folium

st.subheader("🗺 地図")

# ★ここで地図を作る（絶対に最初）
map_obj = folium.Map(location=[35.7, 139.7], zoom_start=5)

for mdata in st.session_state.memories:
    if mdata["lat"] and mdata["lon"]:

        img_html = ""
        if mdata["image"]:
            img_b64 = base64.b64encode(mdata["image"]).decode()
            img_html = f"""
            <br>
            <img src="data:image/jpeg;base64,{img_b64}" width="200">
            """

        popup_html = f"""
        <b>📍場所:</b> {mdata['place']}<br>
        <b>🍽食べたもの:</b> {mdata['food']}<br>
        <b>⭐満足度:</b> {mdata['score']}<br>
        <b>📝メモ:</b> {mdata['memo']}
        {img_html}
        """

        color = "green" if mdata["score"] >= 4 else "orange" if mdata["score"] == 3 else "red"

folium.Marker(
    [mdata["lat"], mdata["lon"]],
    popup=folium.Popup(popup_html, max_width=300),
    icon=folium.Icon(color=color, icon="map-marker", prefix="fa")
).add_to(map_obj)

# ★最後に表示
st_folium(map_obj)
