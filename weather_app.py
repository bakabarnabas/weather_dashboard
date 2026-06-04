import streamlit as st
import requests
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1628 50%, #091220 100%);
        color: #e8eaf6;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1f3c 0%, #0a1628 100%);
        border-right: 1px solid #1e3a5f;
    }
    section[data-testid="stSidebar"] .stTextInput > div > div > input {
        background: #0a1628;
        border: 1px solid #1e4a7a;
        color: #7eb8f7;
        font-family: 'Space Mono', monospace;
        border-radius: 8px;
        padding: 10px 14px;
    }
    section[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
        border-color: #4a9eff;
        box-shadow: 0 0 0 2px rgba(74, 158, 255, 0.2);
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #1a4a8a, #2563eb);
        color: white;
        border: none;
        border-radius: 8px;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        letter-spacing: 1px;
        width: 100%;
        padding: 10px;
        transition: all 0.2s;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
    }

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #0d1f3c 0%, #112244 100%);
        border: 1px solid #1e3a5f;
        border-radius: 16px;
        padding: 24px 20px;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #4a9eff, #60efff);
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(74, 158, 255, 0.15);
    }
    .kpi-icon {
        font-size: 2.2rem;
        margin-bottom: 8px;
        display: block;
    }
    .kpi-value {
        font-family: 'Space Mono', monospace;
        font-size: 2.4rem;
        font-weight: 700;
        color: #60efff;
        line-height: 1;
        margin-bottom: 6px;
    }
    .kpi-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #6b8ab5;
        font-family: 'Space Mono', monospace;
    }
    .kpi-unit {
        font-size: 1rem;
        color: #4a9eff;
        font-family: 'Space Mono', monospace;
    }

    /* City header */
    .city-header {
        background: linear-gradient(135deg, #0d1f3c, #0a2040);
        border: 1px solid #1e3a5f;
        border-radius: 16px;
        padding: 20px 28px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .city-name {
        font-size: 2rem;
        font-weight: 800;
        color: #e8eaf6;
        margin: 0;
        font-family: 'Syne', sans-serif;
    }
    .city-country {
        font-size: 0.85rem;
        color: #4a9eff;
        font-family: 'Space Mono', monospace;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .city-coords {
        font-size: 0.75rem;
        color: #3a5a8a;
        font-family: 'Space Mono', monospace;
        margin-top: 4px;
    }
    .update-time {
        margin-left: auto;
        font-size: 0.75rem;
        color: #3a5a8a;
        font-family: 'Space Mono', monospace;
        text-align: right;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: #0a1628;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
        border: 1px solid #1e3a5f;
    }
    .stTabs [data-baseweb="tab"] {
        color: #6b8ab5;
        font-family: 'Space Mono', monospace;
        font-size: 0.8rem;
        letter-spacing: 1px;
        border-radius: 8px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1a4a8a, #2563eb) !important;
        color: white !important;
    }

    /* Section titles */
    .section-title {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: #3a5a8a;
        font-family: 'Space Mono', monospace;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid #1e3a5f;
    }

    /* History table */
    .stDataFrame {
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        overflow: hidden;
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Sidebar logo area */
    .sidebar-logo {
        text-align: center;
        padding: 20px 0 10px 0;
        margin-bottom: 20px;
        border-bottom: 1px solid #1e3a5f;
    }
    .sidebar-logo span {
        font-size: 3rem;
        display: block;
    }
    .sidebar-logo h2 {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        font-size: 1.1rem;
        color: #7eb8f7;
        margin: 8px 0 0 0;
        letter-spacing: 2px;
    }
</style>
""", unsafe_allow_html=True)


# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH = "weather_log.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS search_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            city       TEXT    NOT NULL,
            temperature REAL,
            humidity   REAL,
            wind_speed REAL,
            searched_at TEXT   NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def log_search(city: str, temperature: float, humidity: float, wind_speed: float):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO search_log (city, temperature, humidity, wind_speed, searched_at) VALUES (?, ?, ?, ?, ?)",
        (city, temperature, humidity, wind_speed, datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()
    conn.close()

def load_history() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT city, temperature, humidity, wind_speed, searched_at FROM search_log ORDER BY id DESC LIMIT 50",
        conn
    )
    conn.close()
    return df

init_db()


# ── API helpers ───────────────────────────────────────────────────────────────
def geocode(city: str):
    """Return (lat, lon, display_name, country) or None on failure."""
    try:
        r = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("results"):
            return None
        res = data["results"][0]
        return res["latitude"], res["longitude"], res["name"], res.get("country", "")
    except Exception:
        return None


def get_weather(lat: float, lon: float):
    """Return current + hourly forecast dict or None."""
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,apparent_temperature",
                "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation_probability",
                "forecast_days": 7,
                "timezone": "auto",
            },
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def wmo_description(code: int) -> str:
    table = {
        0: "Clear sky ☀️", 1: "Mainly clear 🌤️", 2: "Partly cloudy ⛅",
        3: "Overcast ☁️", 45: "Fog 🌫️", 48: "Icy fog 🌫️",
        51: "Light drizzle 🌦️", 53: "Drizzle 🌦️", 55: "Heavy drizzle 🌧️",
        61: "Slight rain 🌧️", 63: "Moderate rain 🌧️", 65: "Heavy rain 🌧️",
        71: "Slight snow 🌨️", 73: "Moderate snow 🌨️", 75: "Heavy snow ❄️",
        77: "Snow grains 🌨️", 80: "Slight showers 🌦️", 81: "Moderate showers 🌧️",
        82: "Violent showers ⛈️", 85: "Snow showers 🌨️", 86: "Heavy snow showers ❄️",
        95: "Thunderstorm ⛈️", 96: "Thunderstorm w/ hail ⛈️", 99: "Thunderstorm w/ heavy hail ⛈️",
    }
    return table.get(code, f"Code {code}")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <span>🌤️</span>
        <h2>WEATHER DASH</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-title">Search</p>', unsafe_allow_html=True)
    city_input = st.text_input("City name", value="Budapest", placeholder="e.g. London, Tokyo…", label_visibility="collapsed")
    search_btn = st.button("▶ GET WEATHER", use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">About</p>', unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.75rem; color:#3a5a8a; font-family:"Space Mono",monospace; line-height:1.8'>
    Data: Open-Meteo API<br>
    Geocoding: Open-Meteo<br>
    Logs: SQLite<br><br>    
    hw_08 · Barnabas Baka
    </div>
    """, unsafe_allow_html=True)


# ── Main content ──────────────────────────────────────────────────────────────
if "weather_data" not in st.session_state:
    st.session_state.weather_data = None
    st.session_state.city_meta = None

if search_btn and city_input.strip():
    with st.spinner("Fetching location…"):
        geo = geocode(city_input.strip())
    if geo is None:
        st.warning(f"⚠️ City **'{city_input}'** not found. Please check the spelling and try again.")
    else:
        lat, lon, city_name, country = geo
        with st.spinner(f"Loading weather for {city_name}…"):
            wd = get_weather(lat, lon)
        if wd is None:
            st.warning("⚠️ Weather data unavailable. The forecast API returned an error.")
        else:
            st.session_state.weather_data = wd
            st.session_state.city_meta = {"name": city_name, "country": country, "lat": lat, "lon": lon}
            # Log to DB
            cur = wd["current"]
            log_search(
                city_name,
                cur["temperature_2m"],
                cur["relative_humidity_2m"],
                cur["wind_speed_10m"],
            )

# ── Show dashboard ────────────────────────────────────────────────────────────
if st.session_state.weather_data and st.session_state.city_meta:
    meta = st.session_state.city_meta
    wd   = st.session_state.weather_data
    cur  = wd["current"]
    hrly = wd["hourly"]

    temp      = cur["temperature_2m"]
    feels     = cur["apparent_temperature"]
    humidity  = cur["relative_humidity_2m"]
    wind      = cur["wind_speed_10m"]
    wcode     = cur["weather_code"]
    wdesc     = wmo_description(wcode)
    updated   = cur["time"].replace("T", " ")

    # City header
    st.markdown(f"""
    <div class="city-header">
        <div>
            <p class="city-name">{meta['name']}</p>
            <p class="city-country">📍 {meta['country']}</p>
            <p class="city-coords">{meta['lat']:.4f}° N, {meta['lon']:.4f}° E</p>
        </div>
        <div style="margin-left:16px; font-size:1.5rem;">{wdesc}</div>
        <div class="update-time">
            🕐 Updated<br>{updated}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI cards
    st.markdown('<p class="section-title">Current Conditions</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "🌡️", f"{temp:.1f}", "°C", "Temperature"),
        (c2, "🤔", f"{feels:.1f}", "°C", "Feels Like"),
        (c3, "💧", f"{humidity:.0f}", "%", "Humidity"),
        (c4, "💨", f"{wind:.1f}", "km/h", "Wind Speed"),
    ]
    for col, icon, val, unit, label in cards:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <span class="kpi-icon">{icon}</span>
                <div class="kpi-value">{val}<span class="kpi-unit">{unit}</span></div>
                <div class="kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs: Forecast + History
    tab1, tab2 = st.tabs(["📈  7-DAY FORECAST", "🗂️  SEARCH HISTORY"])

    with tab1:
        st.markdown('<p class="section-title" style="margin-top:16px">Hourly forecast — next 7 days</p>', unsafe_allow_html=True)

        times = pd.to_datetime(hrly["time"])
        df_h = pd.DataFrame({
            "time": times,
            "temperature": hrly["temperature_2m"],
            "humidity": hrly["relative_humidity_2m"],
            "wind_speed": hrly["wind_speed_10m"],
            "precip_prob": hrly["precipitation_probability"],
        })

        # Temperature + humidity combined chart
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=df_h["time"], y=df_h["temperature"],
            name="Temperature (°C)",
            line=dict(color="#60efff", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(96, 239, 255, 0.06)",
            hovertemplate="%{x|%b %d %H:%M}<br><b>%{y:.1f} °C</b><extra></extra>",
        ))
        fig_temp.add_trace(go.Scatter(
            x=df_h["time"], y=df_h["humidity"],
            name="Humidity (%)",
            yaxis="y2",
            line=dict(color="#4a9eff", width=1.5, dash="dot"),
            hovertemplate="%{x|%b %d %H:%M}<br><b>%{y:.0f} %</b><extra></extra>",
        ))
        fig_temp.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,31,60,0.5)",
            yaxis=dict(title=dict(text="°C", font=dict(color="#60efff")), gridcolor="#1e3a5f", color="#60efff"),
            yaxis2=dict(title=dict(text="%", font=dict(color="#4a9eff")), overlaying="y", side="right", gridcolor="rgba(0,0,0,0)", color="#4a9eff"),
            xaxis=dict(gridcolor="#1e3a5f"),
            legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.05),
            height=320,
            margin=dict(l=0, r=0, t=30, b=0),
            hovermode="x unified",
            font=dict(family="Space Mono, monospace", size=11),
        )
        st.plotly_chart(fig_temp, use_container_width=True, config={"displayModeBar": False})

        # Wind + precipitation row
        col_w, col_p = st.columns(2)
        with col_w:
            st.markdown('<p class="section-title">Wind Speed (km/h)</p>', unsafe_allow_html=True)
            fig_wind = go.Figure()
            fig_wind.add_trace(go.Scatter(
                x=df_h["time"], y=df_h["wind_speed"],
                fill="tozeroy",
                line=dict(color="#a78bfa", width=2),
                fillcolor="rgba(167, 139, 250, 0.07)",
                hovertemplate="%{x|%b %d %H:%M}<br><b>%{y:.1f} km/h</b><extra></extra>",
            ))
            fig_wind.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(13,31,60,0.5)",
                yaxis=dict(gridcolor="#1e3a5f", color="#a78bfa"),
                xaxis=dict(gridcolor="#1e3a5f"),
                height=220,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
                font=dict(family="Space Mono, monospace", size=11),
            )
            st.plotly_chart(fig_wind, use_container_width=True, config={"displayModeBar": False})

        with col_p:
            st.markdown('<p class="section-title">Precipitation Probability (%)</p>', unsafe_allow_html=True)
            fig_prec = go.Figure()
            fig_prec.add_trace(go.Bar(
                x=df_h["time"], y=df_h["precip_prob"],
                marker_color="#34d399",
                opacity=0.7,
                hovertemplate="%{x|%b %d %H:%M}<br><b>%{y:.0f}%</b><extra></extra>",
            ))
            fig_prec.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(13,31,60,0.5)",
                yaxis=dict(gridcolor="#1e3a5f", color="#34d399", range=[0, 100]),
                xaxis=dict(gridcolor="#1e3a5f"),
                height=220,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
                font=dict(family="Space Mono, monospace", size=11),
            )
            st.plotly_chart(fig_prec, use_container_width=True, config={"displayModeBar": False})

    with tab2:
        st.markdown('<p class="section-title" style="margin-top:16px">Last 50 searches (SQLite log)</p>', unsafe_allow_html=True)
        hist = load_history()
        if hist.empty:
            st.info("No searches logged yet.")
        else:
            hist.columns = ["City", "Temp (°C)", "Humidity (%)", "Wind (km/h)", "Searched At"]
            st.dataframe(
                hist,
                use_container_width=True,
                hide_index=True,
            )

else:
    # Welcome state
    st.markdown("""
    <div style='
        text-align:center;
        padding: 80px 40px;
        color: #2a4a7a;
    '>
        <div style='font-size:5rem; margin-bottom:24px'>🌍</div>
        <h2 style='
            font-family: Syne, sans-serif;
            font-size: 2rem;
            font-weight: 800;
            color: #1e3a5f;
            margin-bottom: 12px;
        '>Enter a city name to get started</h2>
        <p style='
            font-family: "Space Mono", monospace;
            font-size: 0.85rem;
            color: #1a3a5a;
            letter-spacing: 1px;
        '>Type a city in the sidebar → click GET WEATHER</p>
    </div>
    """, unsafe_allow_html=True)
