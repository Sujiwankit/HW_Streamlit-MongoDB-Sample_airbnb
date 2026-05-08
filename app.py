import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Airbnb Global Market Insights & Pricing Dashboard",
    page_icon="🏝️",
    layout="wide"
)

COLORS = dict(
    text="#103D36", muted="#2D6B5C", red="#B41A23",
    evergreen="#11584B", copper="#DE8F65", orange="#D96F32",
    teal="#0F6B5B", card="#FFF8F0", border="#DDA47B", gold="#E5B280"
)

PRICE_COLORS = {
    "Low (< $100)": COLORS["evergreen"],
    "Medium ($100-$200)": COLORS["copper"],
    "High ($200-$500)": COLORS["orange"],
    "Luxury (>= $500)": COLORS["red"]
}

ROOM_COLORS = [
    COLORS["red"], COLORS["orange"], COLORS["copper"],
    COLORS["evergreen"], COLORS["teal"], COLORS["gold"]
]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {{
    background:
        radial-gradient(circle at top left, rgba(180,26,35,.18), transparent 26%),
        radial-gradient(circle at bottom right, rgba(17,88,75,.20), transparent 26%),
        linear-gradient(135deg,#8FD3FF 0%,#BEE7FF 18%,#F8D7B5 45%,#DE8F65 72%,#11584B 100%);
    color:{COLORS["text"]};
    font-family:'Inter',sans-serif;
}}

section[data-testid="stSidebar"] {{
    background:linear-gradient(180deg,#34685C 0%,#1E404F 100%) !important;
    border-right:2px solid #F3C99D !important;
    box-shadow:8px 0 28px rgba(0,0,0,.35);
    backdrop-filter:blur(12px);
}}

section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {{
    color:#F6E6D0 !important;
    font-weight:700 !important;
}}

.sidebar-logo {{
    text-align:center;
    padding:12px 4px 22px;
}}

.sidebar-logo-main {{
    font-family:'Playfair Display',serif;
    font-size:30px;
    font-weight:900;
    line-height:1;
    color:#F05050 !important;
}}

.sidebar-logo-sub {{
    font-family:'Playfair Display',serif;
    font-size:17px;
    font-style:italic;
    color:#F3C99D !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background:rgba(30,64,79,.88) !important;
    border:1px solid rgba(243,201,157,.45) !important;
    border-radius:10px !important;
    box-shadow:inset 0 0 10px rgba(0,0,0,.18);
}}

section[data-testid="stSidebar"] span[data-baseweb="tag"],
section[data-testid="stSidebar"] span[data-baseweb="tag"] span {{
    background:#E5E5E5 !important;
    color:#000 !important;
    border:1px solid #CFCFCF !important;
    border-radius:6px !important;
    font-weight:700 !important;
}}

section[data-testid="stSidebar"] div[data-testid="stSlider"] div {{
    color:#F6E6D0 !important;
}}

section[data-testid="stSidebar"] div[data-testid="stSlider"] [role="slider"] {{
    background:#F05050 !important;
    border:2px solid #F05050 !important;
}}

section[data-testid="stSidebar"] div[data-testid="stSlider"] div[data-baseweb="slider"] > div {{
    background:rgba(246,230,208,.25) !important;
}}

.main-title {{
    font-family:'Playfair Display',serif;
    font-size:46px;
    font-weight:900;
    color:{COLORS["text"]};
    margin-bottom:0;
    letter-spacing:-.5px;
}}

.subtitle {{
    font-size:17px;
    color:{COLORS["red"]};
    font-weight:800;
    margin-top:-4px;
    margin-bottom:14px;
}}

.section-title {{
    font-family:'Playfair Display',serif;
    font-size:25px;
    font-weight:900;
    color:{COLORS["red"]};
    margin-top:26px;
    margin-bottom:14px;
    text-shadow:0 1px 2px rgba(255,255,255,.45);
}}

.hero {{
    background:
        linear-gradient(90deg,rgba(17,88,75,.15),rgba(180,26,35,.10)),
        url("https://images.unsplash.com/photo-1516483638261-f4dbaf036963?auto=format&fit=crop&w=2400&q=90");
    background-size:cover;
    background-position:center;
    min-height:360px;
    border-radius:20px;
    border:2px solid rgba(255,255,255,.35);
    box-shadow:0 12px 34px rgba(17,88,75,.22),0 4px 18px rgba(180,26,35,.12);
    margin-bottom:20px;
}}

.top-card,
div[data-testid="stMetric"],
.legend-box {{
    background:linear-gradient(145deg,rgba(255,244,234,.95),rgba(248,215,181,.88));
    border:1px solid {COLORS["border"]};
    border-radius:18px;
    box-shadow:0 10px 28px rgba(17,88,75,.12),0 4px 10px rgba(180,26,35,.08);
}}

.top-card {{
    padding:16px 20px;
    text-align:center;
}}

div[data-testid="stMetric"] {{
    padding:18px;
}}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] div {{
    color:{COLORS["text"]} !important;
    font-weight:900;
}}

div[data-testid="stMetric"] div {{
    font-family:'Playfair Display',serif;
}}

.legend-box {{
    padding:16px;
    margin-top:8px;
}}

.legend-title {{
    font-weight:900;
    color:{COLORS["red"]};
    margin-bottom:8px;
}}

.legend-item {{
    display:flex;
    align-items:center;
    gap:9px;
    margin:6px 0;
    font-size:14px;
    color:{COLORS["text"]};
}}

.dot {{
    width:14px;
    height:14px;
    border-radius:50%;
    display:inline-block;
    border:1px solid rgba(0,0,0,.2);
}}

.footer-mountain {{
    margin-top:20px;
    height:80px;
    background:
        linear-gradient(180deg,rgba(255,245,230,0),rgba(17,88,75,.65)),
        url("https://images.unsplash.com/photo-1516483638261-f4dbaf036963?auto=format&fit=crop&w=2200&q=80");
    background-size:cover;
    background-position:bottom;
    border-top:1px solid {COLORS["border"]};
    border-radius:18px 18px 0 0;
}}

h1,h2,h3,p,label {{
    color:{COLORS["text"]};
}}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="sidebar-logo">
    <div style="font-size:34px;">🏝️</div>
    <div class="sidebar-logo-main">Airbnb</div>
    <div class="sidebar-logo-sub">Global Insights</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 🔎 FILTERS")

@st.cache_resource
def get_client():
    client = MongoClient(st.secrets["MONGO_URI"], serverSelectionTimeoutMS=10000)
    client.admin.command("ping")
    return client

@st.cache_data(ttl=3600)
def load_data(limit=5000):
    projection = {
        "_id": 1, "name": 1, "property_type": 1, "room_type": 1,
        "bedrooms": 1, "beds": 1, "accommodates": 1, "price": 1,
        "cleaning_fee": 1, "extra_people": 1, "number_of_reviews": 1,
        "review_scores.review_scores_rating": 1,
        "address.country": 1, "address.market": 1, "address.suburb": 1,
        "address.location.coordinates": 1, "amenities": 1,
        "availability.availability_365": 1
    }
    data = list(get_client()["sample_airbnb"]["listingsAndReviews"].find({}, projection).limit(limit))
    return pd.json_normalize(data)

def clean_airbnb(df):
    df = df.copy().rename(columns={
        "_id": "id",
        "address.country": "country",
        "address.market": "market",
        "address.suburb": "suburb",
        "address.location.coordinates": "coordinates",
        "review_scores.review_scores_rating": "rating",
        "availability.availability_365": "availability_365"
    })

    base_cols = [
        "name", "country", "market", "property_type", "room_type",
        "price", "rating", "number_of_reviews", "bedrooms", "beds",
        "accommodates", "availability_365", "amenities"
    ]
    for col in base_cols:
        if col not in df.columns:
            df[col] = None

    for col in ["name", "country", "market", "property_type", "room_type"]:
        df[col] = df[col].fillna("Unknown").astype(str)

    num_cols = [
        "price", "cleaning_fee", "extra_people", "bedrooms", "beds",
        "accommodates", "number_of_reviews", "rating", "availability_365"
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str), errors="coerce")

    df["longitude"] = df["coordinates"].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else None)
    df["latitude"] = df["coordinates"].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else None)
    df["amenities_count"] = df["amenities"].apply(lambda x: len(x) if isinstance(x, list) else 0)

    df = df[df["price"].notna() & (df["price"] > 0)]
    df["rating"] = df["rating"].fillna(df["rating"].median())
    df["number_of_reviews"] = df["number_of_reviews"].fillna(0)
    df["accommodates"] = df["accommodates"].fillna(1)

    df["price_level"] = pd.cut(
        df["price"],
        bins=[0, 100, 200, 500, float("inf")],
        labels=["Low (< $100)", "Medium ($100-$200)", "High ($200-$500)", "Luxury (>= $500)"],
        right=False
    ).astype(str)

    df["rating_level"] = pd.cut(
        df["rating"],
        bins=[-1, 60, 70, 80, 90, 101],
        labels=[
            "Below Average (<60)", "Average (60-69)", "Good (70-79)",
            "Very Good (80-89)", "Excellent (>= 90)"
        ],
        right=False
    ).astype(str)

    return df

try:
    df = clean_airbnb(load_data())
    if df.empty:
        st.error("โหลดข้อมูลได้ แต่ไม่มีข้อมูลที่ใช้งานได้หลัง Clean Data")
        st.stop()
except KeyError:
    st.error("ไม่พบ MONGO_URI ในไฟล์ .streamlit/secrets.toml")
    st.code('MONGO_URI = "mongodb+srv://USERNAME:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"')
    st.stop()
except Exception as e:
    st.error("เชื่อมต่อ MongoDB หรือโหลดข้อมูลไม่สำเร็จ")
    st.exception(e)
    st.stop()

def unique_list(col):
    return sorted(df[col].dropna().unique())

selected_country = st.sidebar.multiselect("📍 Select Country", unique_list("country"), default=unique_list("country"))
selected_room = st.sidebar.multiselect("🛏️ Select Room Type", unique_list("room_type"), default=unique_list("room_type"))
selected_property = st.sidebar.multiselect("🏠 Select Property Type", unique_list("property_type"), default=unique_list("property_type"))

price_min, price_max = int(df["price"].min()), int(df["price"].quantile(.95))
if price_min == price_max:
    price_max += 1

selected_price = st.sidebar.slider("🏷️ Price Range (USD)", price_min, price_max, (price_min, price_max))
min_rating = st.sidebar.slider("⭐ Minimum Rating", 0.0, 100.0, 0.0, step=5.0)

filtered_df = df[
    df["country"].isin(selected_country)
    & df["room_type"].isin(selected_room)
    & df["property_type"].isin(selected_property)
    & df["price"].between(selected_price[0], selected_price[1])
    & (df["rating"] >= min_rating)
]

if filtered_df.empty:
    st.warning("ไม่มีข้อมูลตาม Filter ที่เลือก กรุณาปรับ Filter ใหม่")
    st.stop()

top1, top2 = st.columns([4, 1])

with top1:
    st.markdown('<div class="main-title">Airbnb Global Market Insights & Pricing Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Interactive analysis from MongoDB Atlas: sample_airbnb.listingsAndReviews</div>', unsafe_allow_html=True)

with top2:
    now = datetime.now().strftime("%b %d, %Y %I:%M %p")
    st.markdown(f"""
    <div class="top-card">
        <div style="font-size:13px;color:{COLORS["muted"]};font-weight:800;">⏱️ Last Updated</div>
        <div style="font-size:12px;color:{COLORS["text"]};font-weight:700;">{now}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="hero"></div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
k1.metric("🏠 Total Listings", f"{len(filtered_df):,}", "Across selected filters")
k2.metric("💰 Average Price", f"${filtered_df['price'].mean():,.0f}", "Per night")
k3.metric("⭐ Average Rating", f"{filtered_df['rating'].mean():.1f}", "Out of 100")
k4.metric("💬 Average Reviews", f"{filtered_df['number_of_reviews'].mean():.1f}", "Per listing")

def vintage_layout(fig, title_size=18):
    fig.update_layout(
        plot_bgcolor="rgba(255,248,240,.92)",
        paper_bgcolor="rgba(255,248,240,.88)",
        font=dict(color=COLORS["text"], family="Inter", size=12),
        title_font=dict(size=title_size, color=COLORS["red"], family="Playfair Display"),
        margin=dict(l=20, r=20, t=55, b=30),
        legend=dict(
            bgcolor="rgba(255,255,255,.55)",
            bordercolor="rgba(17,88,75,.10)",
            borderwidth=1,
            font=dict(size=12, color=COLORS["text"])
        )
    )
    fig.update_xaxes(gridcolor="rgba(17,88,75,.10)", zerolinecolor="rgba(17,88,75,.10)")
    fig.update_yaxes(gridcolor="rgba(17,88,75,.10)", zerolinecolor="rgba(17,88,75,.10)")
    return fig

def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

def top_count(col, name="listings", n=10):
    return filtered_df.groupby(col).size().reset_index(name=name).sort_values(name, ascending=False).head(n)

scale = [COLORS["evergreen"], COLORS["copper"], COLORS["orange"], COLORS["red"]]

section("🏛️ Market & Room Type Overview")
c1, c2 = st.columns(2)

country_count = top_count("country")
fig_country = px.bar(
    country_count, x="listings", y="country", orientation="h",
    title="Top 10 Countries by Number of Listings",
    color="listings", color_continuous_scale=scale
)
fig_country.update_layout(yaxis=dict(autorange="reversed"))
c1.plotly_chart(vintage_layout(fig_country), use_container_width=True)

room_count = top_count("room_type", n=len(unique_list("room_type")))
fig_room = px.pie(
    room_count, values="listings", names="room_type", hole=.55,
    title="Room Type Distribution", color_discrete_sequence=ROOM_COLORS
)
fig_room.update_traces(textposition="inside", textinfo="percent+label", marker=dict(line=dict(color=COLORS["card"], width=2)))
c2.plotly_chart(vintage_layout(fig_room), use_container_width=True)

section("🏷️ Price & Property Analysis")
c3, c4 = st.columns(2)

property_price = filtered_df.groupby("property_type")["price"].mean().reset_index().sort_values("price", ascending=False).head(12)
fig_prop = px.bar(
    property_price, x="property_type", y="price",
    title="Average Price by Property Type (Top 12)",
    color="price", color_continuous_scale=scale
)
fig_prop.update_layout(xaxis_tickangle=-35)
c3.plotly_chart(vintage_layout(fig_prop), use_container_width=True)

fig_box = px.box(
    filtered_df, x="room_type", y="price",
    title="Price Distribution by Room Type",
    color="room_type", color_discrete_sequence=ROOM_COLORS
)
c4.plotly_chart(vintage_layout(fig_box), use_container_width=True)

section("📈 Rating vs Price Insight & Global Tile Map")
c5, c6 = st.columns([1, 1.35])

sample_plot = filtered_df.sample(n=min(1500, len(filtered_df)), random_state=42)
fig_scatter = px.scatter(
    sample_plot, x="price", y="rating", size="number_of_reviews",
    color="price_level", color_discrete_map=PRICE_COLORS,
    hover_name="name",
    hover_data=["country", "market", "property_type", "room_type", "accommodates"],
    title="Price vs Rating by Price Level"
)
c5.plotly_chart(vintage_layout(fig_scatter), use_container_width=True)

map_df = filtered_df.dropna(subset=["latitude", "longitude"]).sample(
    n=min(2500, len(filtered_df.dropna(subset=["latitude", "longitude"]))),
    random_state=42
)

if len(map_df):
    fig_map = px.scatter_map(
        map_df, lat="latitude", lon="longitude",
        color="price_level", size="accommodates",
        hover_name="name",
        hover_data={
            "country": True, "market": True, "room_type": True,
            "property_type": True, "price": ":,.0f", "rating": ":.1f",
            "latitude": False, "longitude": False
        },
        color_discrete_map=PRICE_COLORS,
        zoom=1, height=540,
        title="Global Airbnb Listings Map | Color = Price Level",
        map_style="carto-positron"
    )
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=55, b=0),
        paper_bgcolor="rgba(255,248,240,.92)",
        font=dict(color=COLORS["text"], family="Inter"),
        title_font=dict(size=18, color=COLORS["red"], family="Playfair Display"),
        legend_title_text="Price Color Guide"
    )
    c6.plotly_chart(fig_map, use_container_width=True)
else:
    c6.warning("ไม่มีข้อมูล latitude / longitude สำหรับแสดงแผนที่")

st.markdown(f"""
<div class="legend-box">
    <div class="legend-title">🎨 Price Color Guide</div>
    <div class="legend-item"><span class="dot" style="background:{PRICE_COLORS["Luxury (>= $500)"]};"></span>สีแดง = Luxury Price ตั้งแต่ $500 ต่อคืนขึ้นไป</div>
    <div class="legend-item"><span class="dot" style="background:{PRICE_COLORS["High ($200-$500)"]};"></span>สีส้ม = High Price ระหว่าง $200 - $500 ต่อคืน</div>
    <div class="legend-item"><span class="dot" style="background:{PRICE_COLORS["Medium ($100-$200)"]};"></span>สี Copper Tan = Medium Price ระหว่าง $100 - $200 ต่อคืน</div>
    <div class="legend-item"><span class="dot" style="background:{PRICE_COLORS["Low (< $100)"]};"></span>สี Evergreen = Low Price ต่ำกว่า $100 ต่อคืน</div>
</div>
""", unsafe_allow_html=True)

section("📊 Advanced Insights")
c7, c8, c9 = st.columns([1.15, 1.15, .75])

fig_amenity = px.scatter(
    filtered_df, x="amenities_count", y="price",
    color="price_level", size="accommodates",
    title="Amenities Count vs Price",
    color_discrete_map=PRICE_COLORS,
    hover_name="name",
    hover_data=["country", "market", "room_type"]
)
c7.plotly_chart(vintage_layout(fig_amenity), use_container_width=True)

review_market = (
    filtered_df.groupby("market")[["number_of_reviews", "rating"]]
    .mean().reset_index().dropna()
    .sort_values("number_of_reviews", ascending=False).head(12)
)
fig_review = px.bar(
    review_market, x="market", y="number_of_reviews",
    color="rating",
    title="Average Reviews by Market | Color = Average Rating",
    color_continuous_scale=scale
)
fig_review.update_layout(xaxis_tickangle=-35)
c8.plotly_chart(vintage_layout(fig_review), use_container_width=True)

rating_order = [
    "Excellent (>= 90)", "Very Good (80-89)", "Good (70-79)",
    "Average (60-69)", "Below Average (<60)"
]
rating_count = filtered_df.groupby("rating_level").size().reset_index(name="count")
rating_count["rating_level"] = pd.Categorical(rating_count["rating_level"], categories=rating_order, ordered=True)
rating_count = rating_count.sort_values("rating_level")

fig_rating = px.bar(
    rating_count, x="count", y="rating_level", orientation="h",
    title="Average Rating Color Guide",
    color="rating_level",
    color_discrete_sequence=[COLORS["red"], COLORS["orange"], COLORS["copper"], COLORS["teal"], COLORS["evergreen"]]
)
fig_rating.update_layout(showlegend=False, yaxis=dict(autorange="reversed"))
c9.plotly_chart(vintage_layout(fig_rating), use_container_width=True)

section("▣ Listing Detail Table (Showing Top 200)")

show_cols = [
    "name", "country", "market", "property_type", "room_type",
    "price", "price_level", "rating", "number_of_reviews",
    "bedrooms", "beds", "accommodates", "amenities_count"
]
show_cols = [c for c in show_cols if c in filtered_df.columns]

st.dataframe(
    filtered_df[show_cols].sort_values("price", ascending=False).head(200),
    use_container_width=True
)

st.markdown("""
<div style="text-align:center;color:#B41A23;font-size:15px;font-weight:800;margin-top:18px;">
Built with ❤️ Streamlit + MongoDB Atlas + Plotly
</div>
<div class="footer-mountain"></div>
""", unsafe_allow_html=True)
