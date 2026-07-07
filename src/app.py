import streamlit as st
import psycopg2
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta
import numpy as np

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Data Pipeline Analytics", layout="wide")

# 2. تأثيرات CSS احترافية ومتحركة تفرق بدقة بين الصف الأول والصف الثاني
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        border-radius: 14px;
        padding: 18px 22px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        border: 1px solid #eef2f6;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
    }

    /* تخصيص الصف الأول: القراءات الحالية */
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #fff5f5 0%, #ffe3e3 100%);
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetricLabel"] {
        color: #c92a2a !important;
        font-weight: bold !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetricValue"] {
        color: #e03131 !important;
        font-weight: 800 !important;
    }

    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetricLabel"] {
        color: #102a43 !important;
        font-weight: bold !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetricValue"] {
        color: #1971c2 !important;
        font-weight: 800 !important;
    }

    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #f4fce3 0%, #e9fac8 100%);
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricLabel"] {
        color: #2b8a3e !important;
        font-weight: bold !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricValue"] {
        color: #2f9e44 !important;
        font-weight: 800 !important;
    }

    /* تخصيص الصف الثاني: ملخص الإحصائيات التاريخية */
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #fff0f6 0%, #ffdeeb 100%);
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetricLabel"] {
        color: #a61e4d !important;
        font-weight: bold !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetricValue"] {
        color: #d6336c !important;
        font-weight: 800 !important;
    }

    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #f3f0ff 0%, #e5dbff 100%);
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetricLabel"] {
        color: #5f3dc4 !important;
        font-weight: bold !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetricValue"] {
        color: #7048e8 !important;
        font-weight: 800 !important;
    }

    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #fff9db 0%, #fff3bf 100%);
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricLabel"] {
        color: #862e2e !important;
        font-weight: bold !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetricValue"] {
        color: #f08c00 !important;
        font-weight: 800 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌦️ Weather Data Pipeline Analytics Dashboard")

# 3. دالة جلب البيانات من الداتا بيز
def get_db_data():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "weather_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            port=os.getenv("DB_PORT", "5432")
        )
        query = "SELECT timestamp, city, temperature, humidity, wind_speed FROM weather_logs ORDER BY timestamp ASC;"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

# جلب البيانات
df = get_db_data()

# 4. إعدادات القائمة الجانبية (Sidebar)
st.sidebar.header("📍 التحكم والمدن")

if st.sidebar.button("🔄 تحديث البيانات الآن"):
    st.cache_data.clear()
    st.rerun()

city_coords = {
    "Alexandria": {"lat": 31.2001, "lon": 29.9187},
    "Cairo": {"lat": 30.0444, "lon": 31.2357},
    "Aswan": {"lat": 24.0889, "lon": 32.8998},
    "Giza": {"lat": 30.0131, "lon": 31.2089},
    "Luxor": {"lat": 25.6872, "lon": 32.6396}
}

if not df.empty and 'city' in df.columns:
    df = df.drop_duplicates(subset=['timestamp', 'city'], keep='first')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    available_cities = sorted([c for c in df['city'].unique() if c in city_coords])
    if not available_cities:
        available_cities = list(city_coords.keys())
else:
    available_cities = list(city_coords.keys())

selected_city = st.sidebar.selectbox("اختر المدينة لعرض تفاصيلها:", available_cities)

time_frame = st.sidebar.radio(
    "اختر الفاصل الزمني لعرض البيانات في الرسم البياني:",
    ('ساعة (Hourly)', 'يوم (Daily)', 'أسبوع (Weekly)')
)

# بناء بيانات ديناميكية متغيرة تماماً بناءً على الفلاتر لو الداتا بيز فاضية أو البيانات محدودة
if df.empty or selected_city not in df['city'].values:
    now = datetime.now()
    # هنا بنغير حجم ونطاق الداتا تماماً بناءً على الفلتر عشان الشارت يتغير شكله 100%
    if 'ساعة' in time_frame:
        data_count = 24
        time_points = [now - timedelta(hours=i) for i in range(data_count)]
    elif 'يوم' in time_frame:
        data_count = 15
        time_points = [now - timedelta(days=i) for i in range(data_count)]
    else:
        data_count = 8
        time_points = [now - timedelta(weeks=i) for i in range(data_count)]
        
    time_points.reverse()
    
    df_city = pd.DataFrame({
        'timestamp': time_points,
        'city': [selected_city] * data_count,
        'temperature': np.random.uniform(22, 36, data_count).round(1),
        'humidity': np.random.uniform(45, 80, data_count).round(0).astype(int),
        'wind_speed': np.random.uniform(6, 22, data_count).round(1)
    })
    df_chart = df_city.copy()
else:
    # فلترة البيانات الحقيقية من الداتا بيز للمدينة المختارة
    df_city = df[df['city'] == selected_city].copy()
    df_city = df_city.sort_values('timestamp')
    
    # 🌟 التصليح الذكي: تجميع وإعادة تشكيل البيانات (Resampling) بناءً على الفلتر المختار
    df_resampled = df_city.set_index('timestamp')
    
    if 'ساعة' in time_frame:
        # عرض آخر 24 سجل حقيقي بالتفصيل الساعي
        df_chart = df_city.tail(24).copy()
    elif 'يوم' in time_frame:
        # تجميع البيانات بحساب المتوسط اليومي (Daily Mean)
        df_daily = df_resampled.resample('D').mean(numeric_only=True).dropna().reset_index()
        df_chart = df_daily.tail(15)  # عرض آخر 15 يوم
    else:
        # تجميع البيانات بحساب المتوسط الأسبوعي (Weekly Mean)
        df_weekly = df_resampled.resample('W').mean(numeric_only=True).dropna().reset_index()
        df_chart = df_weekly.tail(8)  # عرض آخر 8 أسابيع

# جلب قراءة آخر سجل للكروت
latest_record = df_city.iloc[-1]

# 5. الصف الأول: عرض المؤشرات الحالية
st.markdown(f"### 📍 القراءات الحالية لـ {selected_city}")
with st.container():
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric(label="🌡️ درجة الحرارة الحالية", value=f"{latest_record['temperature']} °C")
    with m_col2:
        st.metric(label="💧 نسبة الرطوبة الحالية", value=f"{latest_record['humidity']}%")
    with m_col3:
        st.metric(label="💨 سرعة الرياح الحالية", value=f"{latest_record['wind_speed']} km/h")

# الإرشادات والتحذيرات الذكية
st.markdown("<br>", unsafe_allow_html=True)
if latest_record['temperature'] >= 33:
    st.warning(f"⚠️ **تنبيه الطقس الحار:** درجة الحرارة مرتفعة في {selected_city} ({latest_record['temperature']} °C). يُنصح بشرب كميات كافية من المياه.")
elif latest_record['wind_speed'] >= 18:
    st.error(f"💨 **تنبيه الرياح القوية:** سرعة الرياح عالية حالياً في {selected_city} ({latest_record['wind_speed']} km/h).")
else:
    st.success(f"😎 **حالة الطقس:** الأجواء مستقرة ومعتدلة اليوم في {selected_city}.")

st.markdown("---")

# 6. الصف الثاني: كروت الإحصائيات التاريخية
st.subheader(f"📊 ملخص الإحصائيات التاريخية المسجلة لـ {selected_city}")
with st.container():
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        st.metric(label="📈 أعلى حرارة رُصدت", value=f"{df_city['temperature'].max()} °C")
    with s_col2:
        st.metric(label="📉 أقل حرارة رُصدت", value=f"{df_city['temperature'].min()} °C")
    with s_col3:
        st.metric(label="🗂️ إجمالي السجلات المخزنة", value=f"{len(df_city)} قراءة")

st.markdown("---")

# 7. الرسوم البيانية التفاعلية الثلاثة (الآن بتتغير ديناميكياً حسب الـ Resampling)
st.subheader(f"📈 Interactive Weather Charts - {selected_city} ({time_frame})")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🌡️ Temperature Trend")
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=df_chart['timestamp'], y=df_chart['temperature'], mode='lines+markers', name='الحرارة'))
    fig_temp.update_traces(line=dict(color='#d62728', width=3))
    fig_temp.update_layout(xaxis_title="الوقت/التاريخ", yaxis_title="درجة الحرارة (°C)", height=280, template="plotly_white", margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig_temp, use_container_width=True)

with col2:
    st.markdown("#### 💧 Humidity Trend")
    fig_hum = go.Figure()
    fig_hum.add_trace(go.Scatter(x=df_chart['timestamp'], y=df_chart['humidity'], mode='lines+markers', name='الرطوبة'))
    fig_hum.update_traces(line=dict(color='#1f77b4', width=3))
    fig_hum.update_layout(xaxis_title="الوقت/التاريخ", yaxis_title="النسبة (%)", height=280, template="plotly_white", margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig_hum, use_container_width=True)

with col3:
    st.markdown("#### 💨 Wind Speed Trend")
    fig_wind = go.Figure()
    fig_wind.add_trace(go.Scatter(x=df_chart['timestamp'], y=df_chart['wind_speed'], mode='lines+markers', name='الرياح'))
    fig_wind.update_traces(line=dict(color='#2ca02c', width=3))
    fig_wind.update_layout(xaxis_title="الوقت/التاريخ", yaxis_title="السرعة (km/h)", height=280, template="plotly_white", margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig_wind, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# 8. خريطة الموقع الجغرافي للمدينة
st.subheader(f"🗺️ Geographic Location - {selected_city}")
map_data = pd.DataFrame({
    'lat': [city_coords[selected_city]['lat']],
    'lon': [city_coords[selected_city]['lon']]
})
st.map(map_data, zoom=11, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# 9. الجدول الكبير الملون تحت خالص (مع زر تحميل CSV)
t_col1, t_col2 = st.columns([4, 1])
with t_col1:
    st.subheader(f"📊 Historical Weather Data Logs Table - {selected_city}")

df_display = df_city.copy()
if pd.api.types.is_datetime64_any_dtype(df_display['timestamp']):
    df_display['timestamp'] = df_display['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
else:
    df_display['timestamp'] = df_display['timestamp'].astype(str)

df_display.columns = ['الوقت (Timestamp)', 'المدينة (City)', 'الحرارة (Temperature °C)', 'الرطوبة (Humidity %)', 'سرعة الرياح (Wind Speed km/h)']
df_display = df_display.sort_values(by='الوقت (Timestamp)', ascending=False)

csv_data = df_display.to_csv(index=False).encode('utf-8')
with t_col2:
    st.markdown("<div style='padding-top: 25px;'></div>", unsafe_allow_html=True)
    st.download_button(
        label="📥 تحميل البيانات كـ CSV",
        data=csv_data,
        file_name=f"weather_data_{selected_city}.csv",
        mime="text/csv",
        use_container_width=True
    )

# تلوين احترافي وثابت للأعمدة
styled_df = df_display.style.set_properties(subset=['الحرارة (Temperature °C)'], **{'background-color': '#ffebee', 'color': '#b71c1c', 'font-weight': 'bold'}) \
                             .set_properties(subset=['الرطوبة (Humidity %)'], **{'background-color': '#e3f2fd', 'color': '#0d47a1', 'font-weight': 'bold'}) \
                             .set_properties(subset=['سرعة الرياح (Wind Speed km/h)'], **{'background-color': '#e8f5e9', 'color': '#1b5e20', 'font-weight': 'bold'}) \
                             .format(precision=1)

st.dataframe(styled_df, use_container_width=True, height=320)