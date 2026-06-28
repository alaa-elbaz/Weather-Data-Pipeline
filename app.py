import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

st.set_page_config(page_title="Weather Dashboard", layout="wide")

st.title("🌦️ Automated Multi-City Weather Data Pipeline")
st.subheader("عرض حي ومؤتمت لبيانات الطقس لمدن متعددة")

# إعدادات الاتصال ثابتة وصريحة لشبكة الدوكر الداخلية
# استخدام الـ Gateway السحري للدوكر للوصول لجهازك ومنه لقاعدة البيانات فوراً
# استخدام الـ Gateway السحري المباشر
db_host = os.getenv("DB_HOST", "host.docker.internal")
db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("DB_PASSWORD", "postgres")
db_name = os.getenv("DB_NAME", "weather_db")
db_port = os.getenv("DB_PORT", "5432")

db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

try:
    engine = create_engine(db_url)
    # جلب البيانات من الجدول الأساسي
    df = pd.read_sql("SELECT * FROM weather_logs", engine)
    
    if not df.empty:
        st.success("✅ تم تحميل البيانات بنجاح من قاعدة البيانات!")
        
        # فلاتر المدن في القائمة الجانبية
        st.sidebar.header("الفلاتر")
        city = st.sidebar.selectbox("اختر المدينة:", df['city'].unique())
        city_df = df[df['city'] == city]
        
        # عرض المقاييس الأساسية لأحدث قراءة
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label=f"آخر درجة حرارة في {city}", value=f"{city_df['temperature'].iloc[-1]} °C")
        with col2:
            st.metric(label="الرطوبة", value=f"{city_df['humidity'].iloc[-1]} %")
        with col3:
            st.metric(label="سرعة الرياح", value=f"{city_df['wind_speed'].iloc[-1]} km/h")
            
        # عرض الموقع الجغرافي
        st.subheader("📍 الموقع الجغرافي للمدينة")
        # تأمين الخريطة برينام بسيط للأعمدة لو تطلب الأمر
        map_df = city_df[['latitude', 'longitude']].rename(columns={'latitude': 'lat', 'longitude': 'lon'})
        st.map(map_df)
        
        # عرض السجل التاريخي
        st.subheader("📊 سجل البيانات التاريخي")
        st.dataframe(city_df.sort_values(by='timestamp', ascending=False))
    else:
        st.warning("⚠️ قاعدة البيانات فارغة، تأكدي من تشغيل سكريبت الـ ETL وضخ البيانات.")

except Exception as e:
    st.info("💡 بانتظار استقرار قاعدة البيانات وضخ بيانات المدن...")
    st.error(f"تفاصيل الاتصال الحالي: جاري المحاولة على Host: ({db_host}) | الخطأ: {e}")