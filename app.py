import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Weather Dashboard", layout="wide")

st.title("🌦️ Automated Multi-City Weather Data Pipeline")
st.subheader("عرض حي ومؤتمت لبيانات الطقس لمدن متعددة")

# إعدادات الاتصال - مرنة للـ Local والـ Docker
db_host = os.getenv('DB_HOST', 'localhost')
if db_host == 'db' and not os.path.exists('/.dockerenv'):
    db_host = 'localhost'

db_host = 'localhost'
db_user = 'postgres'
db_password = 'postgres' # تثبيت نفس الباسورد ليتطابق مع الـ Pipeline
db_name = 'weather_db'
db_port = '5432'

db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

try:
    engine = create_engine(db_url)
    # جلب البيانات من الجدول
    df = pd.read_sql("SELECT * FROM weather_logs", engine)
    
    if not df.empty:
        st.success("✅ تم تحميل البيانات بنجاح من قاعدة البيانات!")
        
        # فلتر المدن
        st.sidebar.header("الفلاتر")
        city = st.sidebar.selectbox("اختر المدينة:", df['city'].unique())
        city_df = df[df['city'] == city]
        
        # عرض البيانات والمقاييس
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label=f"آخر درجة حرارة في {city}", value=f"{city_df['temperature'].iloc[-1]} °C")
        with col2:
            st.metric(label="الرطوبة", value=f"{city_df['humidity'].iloc[-1]} %")
        with col3:
            st.metric(label="سرعة الرياح", value=f"{city_df['wind_speed'].iloc[-1]} km/h")
            
        # عرض الخريطة التفاعلية والجدول
        st.subheader("📍 الموقع الجغرافي للمدينة")
        st.map(city_df)
        
        st.subheader("📊 سجل البيانات التاريخي")
        st.dataframe(city_df.sort_values(by='timestamp', ascending=False))
    else:
        st.warning("⚠️ قاعدة البيانات فارغة، تأكدي من تشغيل سكريبت الـ ETL.")
except Exception as e:
    # قفلنا القوس هنا وزودنا طباعة الخطأ الحقيقي عشان لو فيه مشكلة تظهر لنا فوراً بدل الرسالة العامة
    st.info("💡 بانتظار تشغيل قاعدة البيانات وضخ بيانات المدن... (تأكدي من تشغيل الحاويات الآن)")
    st.error(f"تفاصيل الخطأ الحالي للـ Connection: {e}")