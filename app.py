import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# تحميل الإعدادات
load_dotenv()

# إعدادات الصفحة
st.set_page_config(page_title="Weather Dashboard", layout="wide")

st.title("🌦️ Weather Data Pipeline Dashboard")
st.markdown("عرض حي لبيانات الطقس المسحوبة من Open-Meteo API")

def get_data():
    # الاتصال بالقاعدة (localhost حالياً)
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@localhost:5432/{os.getenv('DB_NAME')}"
    engine = create_engine(db_url)
    return pd.read_sql("SELECT * FROM weather_logs ORDER BY timestamp DESC", engine)

try:
    df = get_data()

    # 1. عرض ملخص سريع (Metrics)
    col1, col2, col3 = st.columns(3)
    col1.metric("آخر درجة حرارة", f"{df['temperature'].iloc[0]} °C")
    col2.metric("متوسط الرطوبة", f"{df['humidity'].mean():.1f} %")
    col3.metric("سرعة الرياح", f"{df['wind_speed'].iloc[0]} km/h")

    # 2. رسم بياني لتغير الحرارة
    st.subheader("📈 تغير درجات الحرارة خلال الوقت")
    st.line_chart(df.set_index('timestamp')['temperature'])

    # 3. عرض الجدول الكامل
    st.subheader("📋 البيانات الخام")
    st.dataframe(df)

except Exception as e:
    st.warning("بانتظار تشغيل قاعدة البيانات لرؤية البيانات... (شغلي Docker أولاً)")