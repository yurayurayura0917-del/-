import streamlit as st
import json
import os
import pandas as pd
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import base64
from PIL import Image
import io

geolocator = Nominatim(user_agent="memory_app")

def save_data():
    with open("memories.json", "w") as f:
        json.dump(st.session_state.memories, f)

# =====================
# データ保存（簡易）
# =====================
if "memories" not in st.session_state:
    if os.path.exists("memories.json"):
        with open("memories.json", "r") as f:
            st.session_state.memories = json.load(f)
    else:
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
        img_base64 = base64.b64encode(img_bytes).decode()

    st.session_state.memories.append({
        "place": place,
        "food": food,
        "score": score,
        "memo": memo,
        "lat": lat,
        "lon": lon,
        "image": img_base64
    })
    
    save_data()
    
    st.success("保存したよ！")

# =====================
# 一覧
# =====================
st.subheader("📚 思い出一覧")

for i, m in enumerate(st.session_state.memories):

    st.markdown(f"""
    <div style="
        background:#ffffff;
        padding:15px;
        margin:10px 0;
        border-radius:12px;
        box-shadow:0 2px 6px rgba(0,0,0,0.1);
    ">
        <h4>📍 {m['place']}</h4>
        <p>🍽 {m['food']}　⭐ {m['score']}</p>
        <p>📝 {m['memo']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if m["image"]:
        img_bytes = base64.b64decode(m["image"])
        st.image(img_bytes, width=200)

    if st.button(f"削除{i}"):
        st.session_state.memories.pop(i)
        save_data()
        st.rerun()

# =====================
# 地図
# =====================
import base64
import folium
from streamlit_folium import st_folium

st.subheader("🗺 地図")

map_obj = folium.Map(location=[35.7, 139.7], zoom_start=5)

for mdata in st.session_state.memories:

    lat = mdata.get("lat")
    lon = mdata.get("lon")

    if lat is None or lon is None:
        continue

    img_html = ""
    if mdata.get("image"):
        img_b64 = base64.b64encode(mdata["image"]).decode()
        img_html = f"""
        <br>
        <img src="data:image/jpeg;base64,{img_b64}" width="200">
        """

    popup_html = f"""
    <div style="width:220px">
        <b>📍場所:</b> {mdata.get('place','')}<br>
        <b>🍽食べたもの:</b> {mdata.get('food','')}<br>
        <b>⭐満足度:</b> {mdata.get('score','')}<br>
        <b>📝メモ:</b> {mdata.get('memo','')}
        {img_html}
    </div>
    """

    folium.Marker(
        [lat, lon],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color="red", icon="map-marker", prefix="fa")
    ).add_to(map_obj)

st_folium(map_obj)
