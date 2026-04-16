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
import uuid

geolocator = Nominatim(user_agent="memory_app")

def save_data():
    with open("memories.json", "w") as f:
        json.dump(st.session_state.memories, f)

def get_place_candidates(query):
    try:
        locations = geolocator.geocode(query + ", Japan", exactly_one=False, limit=5)
        return locations
    except:
        return []

# =====================
# データ保存（簡易）
# =====================
import os

if "memories" not in st.session_state:
    if os.path.exists("memories.json"):
        try:
            with open("memories.json", "r") as f:
                st.session_state.memories = json.load(f)
        except:
            st.session_state.memories = []
    else:
        st.session_state.memories = []

for m in st.session_state.memories:
    if "id" not in m:
        m["id"] = str(uuid.uuid4())
        
# =====================
# タイトル
# =====================
st.title("📍 ゆらの思い出アプリ")

if "liked" not in st.session_state:
    st.session_state.liked = set()

# =====================
# 入力
# =====================
query = st.text_input("場所")

candidates = []
selected = None

if query:
    candidates = get_place_candidates(query)

options = []
if candidates:
    options = [loc.address for loc in candidates]
    selected = st.selectbox("候補から選択", options)
    
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
    lat, lon = None, None
    place = query  # デフォルト

    if candidates and selected:
        for loc in candidates:
            if loc.address == selected:
                lat = loc.latitude
                lon = loc.longitude
                place = selected  # ←選んだ住所を保存
                break
                
    img_bytes = None
    
    if image:
        img_bytes = image.read()
        img_base64 = base64.b64encode(img_bytes).decode()

    st.session_state.memories.append({
        "id": str(uuid.uuid4()),
        "place": place,
        "food": food,
        "score": score,
        "memo": memo,
        "lat": lat,
        "lon": lon,
        "image": img_base64,
        "likes": 0
    })
    
    save_data()
    
    st.success("保存したよ！")

search = st.text_input("🔍 検索（場所・メモ・食べ物）")

st.subheader("🔥 人気ランキング")

sorted_memories = sorted(
    st.session_state.memories,
    key=lambda x: x.get("likes", 0),
    reverse=True
)

for m in sorted_memories[:3]:
    st.write(f"📍{m['place']} ❤️{m.get('likes',0)}")

# =====================
# 一覧
# =====================
st.subheader("📚 思い出一覧")

filtered = [
    m for m in st.session_state.memories
    if search.lower() in m["place"].lower()
    or search.lower() in m["memo"].lower()
    or search.lower() in m["food"].lower()
]

for i, m in enumerate(sorted_memories):

    # 🟦カード（情報）
    st.markdown(f"""
    <div style="
        background:#ffffff;
        padding:18px;
        margin:15px 0;
        border-radius:16px;
        box-shadow:0 4px 12px rgba(0,0,0,0.08);
    ">
        <div style="font-size:18px; font-weight:bold;">
            📍 {m['place']}
        </div>
        <div style="margin-top:5px; color:#555;">
            🍽 {m['food']}　⭐ {m['score']}
        </div>
        <div style="margin-top:8px; font-size:14px;">
            📝 {m['memo']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 🟦画像
    if m["image"]:
        img_bytes = base64.b64decode(m["image"])
        st.image(img_bytes, use_container_width=True)

    # 🟦ボタン（下に配置）
    col1, col2 = st.columns([1, 4])

    with col1:
        liked = m["id"] in st.session_state.liked

        if st.button(
            f"{'💔' if liked else '❤️'} {m.get('likes',0)}",
            key=f"like_{m['id']}"
        ):
            if liked:
                m["likes"] = max(0, m["likes"] - 1)
                st.session_state.liked.remove(m["id"])
            else:
                m["likes"] = m.get("likes", 0) + 1
                st.session_state.liked.add(m["id"])

            save_data()
            st.rerun()

    with col2:
        if st.button(f"削除{i}", key=f"delete_{m['id']}"):
            st.session_state.memories.remove(m)
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
        img_b64 = mdata["image"]
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
