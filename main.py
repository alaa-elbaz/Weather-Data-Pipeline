import requests
import pandas as pd
import os
import logging
from sqlalchemy import create_engine
from datetime import datetime
from dotenv import load_dotenv
import schedule
import time

load_dotenv()

logging.basicConfig(
    filename='pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 1. تعريف المدن مع إحداثياتها الجغرافية
CITIES = {
    'Cairo': {'lat': 30.0444, 'lon': 31.2357},
    'Alexandria': {'lat': 31.2001, 'lon': 29.9187},
    'Aswan': {'lat': 24.0889, 'lon': 32.8998}
}

# 2. جلب البيانات من الـ API
def get_weather_data(city_name, lat, lon):
    logging.info(f"⏳ Extracting data for {city_name} from Open-Meteo API...")
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relativehumidity_2m,windspeed_10m&timezone=Africa/Cairo"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() 
        logging.info(f"✅ Data extracted successfully for {city_name}.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ API Connection Error for {city_name}: {e}")
        return None

# 3. معالجة وتحويل البيانات (Transformation)
# 3. معالجة وتحويل البيانات والتحقق من جودتها (Transformation & Validation)
def process_data(json_data, city_name, lat, lon):
    if json_data is None:
        return None
    try:
        hourly_data = json_data['hourly']
        df = pd.DataFrame(hourly_data)
        df['time'] = pd.to_datetime(df['time'])
        df.columns = ['timestamp', 'temperature', 'humidity', 'wind_speed']
        
        # ─── 🛡️ مرحلة مراقبة جودة البيانات (DATA VALIDATION BLOCK) ───
        
        # 1. فحص منطقية درجات الحرارة (مقبول بين -10 و 60 درجة مئوية في مصر)
        invalid_temp = df[(df['temperature'] < -10) | (df['temperature'] > 60)]
        if not invalid_temp.empty:
            logging.warning(f"⚠️ [Data Quality Alert] Detected {len(invalid_temp)} rows with anomalous temperature in {city_name}!")
            
        # 2. فحص الرطوبة (يجب أن تكون دائماً بين 0% و 100%)
        invalid_humidity = df[(df['humidity'] < 0) | (df['humidity'] > 100)]
        if not invalid_humidity.empty:
            logging.warning(f"⚠️ [Data Quality Alert] Detected {len(invalid_humidity)} rows with impossible humidity in {city_name}!")
            
        # 3. فحص سرعة الرياح (لا يمكن أن تكون بالسالب)
        invalid_wind = df[df['wind_speed'] < 0]
        if not invalid_wind.empty:
            logging.warning(f"⚠️ [Data Quality Alert] Detected {len(invalid_wind)} rows with negative wind speed in {city_name}!")

        # 🔄 فلترة البيانات: الاحتفاظ فقط بالسجلات السليمة 100% واستبعاد التالفة
        valid_df = df[
            (df['temperature'] >= -10) & (df['temperature'] <= 60) &
            (df['humidity'] >= 0) & (df['humidity'] <= 100) &
            (df['wind_speed'] >= 0)
        ].copy()

        # حساب عدد الصفوف المستبعدة إن وجدت
        dropped_rows = len(df) - len(valid_df)
        if dropped_rows > 0:
            logging.error(f"❌ [Data Validation Failed] Dropped {dropped_rows} anomalous rows for {city_name} to preserve DB integrity.")
        
        if valid_df.empty:
            return None

        # إضافة البيانات التعريفية (Metadata) للمدينة
        valid_df['city'] = city_name
        valid_df['latitude'] = lat
        valid_df['longitude'] = lon
        valid_df['created_at'] = datetime.now()
        
        logging.info(f"⚡ Transformation & Validation complete for {city_name}. Clean Rows: {len(valid_df)}")
        return valid_df
        
    except Exception as e:
        logging.error(f"❌ Data Transformation Error for {city_name}: {e}")
        return None

# 4. حفظ البيانات في قاعدة البيانات
def save_to_db(df):
    if df is None or df.empty:
        return

    # التعديل الحاسم هنا: تثبيت الإعدادات صراحة لتطابق الـ Dashboard والـ Docker
    db_host = 'localhost'  
    db_user = 'postgres'
    db_password = 'postgres' # تثبيت الباسورد صراحة
    db_name = 'weather_db'
    db_port = '5432'

    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        engine = create_engine(db_url)
        # إنشاء الجدول وضخ البيانات
        df.to_sql('weather_logs', engine, if_exists='append', index=False)
        logging.info(f"💾 Successfully committed {len(df)} rows to PostgreSQL.")
    except Exception as e:
        logging.error(f"❌ Database Load Error: {e}")
        print(f"❌ Database Connection Error: {e}")

# 5. تشغيل الـ Pipeline بالكامل للمدن
def run_etl_pipeline():
    logging.info("⏰ بدء تشغيل الـ Multi-City ETL Pipeline...")
    print(f"⏰ Pipeline started at: {datetime.now()}")
    
    all_city_dfs = []
    for city_name, coords in CITIES.items():
        raw_data = get_weather_data(city_name, coords['lat'], coords['lon'])
        clean_df = process_data(raw_data, city_name, coords['lat'], coords['lon'])
        if clean_df is not None:
            all_city_dfs.append(clean_df)
            
    if all_city_dfs:
        final_df = pd.concat(all_city_dfs, ignore_index=True)
        save_to_db(final_df)
        print("🚀 Multi-city data saved to PostgreSQL successfully!")
    else:
        print("❌ Pipeline execution failed for all cities.")

if __name__ == "__main__":
    # تشغيل الـ Pipeline مرة واحدة صريحة بناءً على أمر الـ Orchestrator
    run_etl_pipeline()
    print("✨ ETL Task executed successfully and finished.")