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

if "page" not in st.session_state:
    st.session_state.page = "home"

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

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

def get_lat_lon(place_name):
    try:
        loc = geolocator.geocode(place_name + ", Japan")
        if loc:
            return loc.latitude, loc.longitude
    except:
        pass
    return None, None

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
st.title("📍 おいしいお店保存するアプリ")

st.markdown("""
    <style>
    button[kind="secondary"] {
        border-radius: 50%;
    }
    </style>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 8])

with col1:
    if st.button("📚"):
        st.session_state.page = "home"
        st.rerun()

with col2:
    if st.button("🗺"):
        st.session_state.page = "map"
        st.rerun()

with col3:
    if st.button("＋"):
        st.session_state.page = "add"
        st.rerun()

# =====================
# 入力
# =====================
if st.session_state.page == "add":
    st.subheader("📍 思い出を追加")

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
    image = st.file_uploader("写真")

    if st.button("保存"):
        lat, lon = None, None
        place = query

        if candidates and selected:
            for loc in candidates:
                if loc.address == selected:
                    lat = loc.latitude
                    lon = loc.longitude
                    place = selected
                    break

        img_base64 = None
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
        st.session_state.page = "home"
        st.rerun()

    if st.button("戻る"):
        st.session_state.page = "home"
        st.rerun()

# 地図
elif st.session_state.page == "map":
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

 # 一覧
elif st.session_state.page == "home":
    
    st.subheader("🔥 人気ランキング")

    sorted_memories = sorted(
        st.session_state.memories,
        key=lambda x: x.get("likes", 0),
        reverse=True
    )

    for m in sorted_memories[:3]:
        st.write(f"📍{m['place']} ❤️{m.get('likes',0)}")

    search = st.text_input("🔍 検索")

    filtered = [
        m for m in st.session_state.memories
        if search.lower() in m["place"].lower()
        or search.lower() in m["memo"].lower()
        or search.lower() in m["food"].lower()
    ]

    st.subheader("📚 思い出一覧")

    filtered = [
        m for m in st.session_state.memories
        if search.lower() in m["place"].lower()
        or search.lower() in m["memo"].lower()
        or search.lower() in m["food"].lower()
    ]

    for m in filtered:

        # 画像
        img_html = ""
        if m.get("image"):
            img_html = f"""
            <img src="data:image/png;base64,{m['image']}"
            style="width:100%; border-radius:12px; margin-bottom:8px;">
            """

        # カード
        st.markdown(
        f"""
    <div style="
        background:#fff;
        border-radius:14px;
        margin:10px 0;
        overflow:hidden;
        box-shadow:0 2px 6px rgba(0,0,0,0.08);
    ">

    <img src="data:image/png;base64,{m['image']}"
    style="width:100%; display:block;">

    <div style="padding:10px 12px;">
        <div style="font-weight:bold;">📍 {m['place']}</div>
        <div style="font-size:13px; color:#666;">
            🍽 {m['food']}　⭐ {m['score']}
        </div>
        <div style="font-size:13px; margin-top:4px;">
            {m['memo']}
        </div>
    </div>

    </div>
    """,
        unsafe_allow_html=True
    )

        col1, col2 = st.columns([1, 4])

        with col1:
            if st.button(f"❤️ {m.get('likes',0)}", key=f"like_{m['id']}"):
                m["likes"] += 1
                save_data()
                st.rerun()

        with col2:
            if st.button("🗑", key=f"delete_{m['id']}"):
                st.session_state.memories.remove(m)
                save_data()
                st.rerun()

