import requests
import pandas as pd
import os
import logging
from sqlalchemy import create_engine
from datetime import datetime
from dotenv import load_dotenv

# استدعاء دالة التحليلات المتقدمة من السكريبت الآخر
from analysis import run_advanced_analytics

# تحميل متغيرات البيئة الآمنة
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

# دالة إرسال التنبيهات عبر التليجرام عند حدوث خطأ
def send_alert(error_message):
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials missing in environment variables.")
        return
        
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message = (
        f"🚨 *Pipeline Failure Alert!*\n\n"
        f"📅 *Timestamp:* {timestamp}\n"
        f"❌ *Error Details:* `{error_message}`\n\n"
        f"⚠️ Please check the container logs ASAP."
    )
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Alert sent to Telegram successfully!")
        else:
            print(f"Failed to send Telegram alert. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending alert to Telegram: {e}")

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
        invalid_temp = df[(df['temperature'] < -10) | (df['temperature'] > 60)]
        if not invalid_temp.empty:
            logging.warning(f"⚠️ [Data Quality Alert] Detected {len(invalid_temp)} rows with anomalous temperature in {city_name}!")
            
        invalid_humidity = df[(df['humidity'] < 0) | (df['humidity'] > 100)]
        if not invalid_humidity.empty:
            logging.warning(f"⚠️ [Data Quality Alert] Detected {len(invalid_humidity)} rows with impossible humidity in {city_name}!")
            
        invalid_wind = df[df['wind_speed'] < 0]
        if not invalid_wind.empty:
            logging.warning(f"⚠️ [Data Quality Alert] Detected {len(invalid_wind)} rows with negative wind speed in {city_name}!")

        # 🔄 فلترة البيانات
        valid_df = df[
            (df['temperature'] >= -10) & (df['temperature'] <= 60) &
            (df['humidity'] >= 0) & (df['humidity'] <= 100) &
            (df['wind_speed'] >= 0)
        ].copy()

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

    db_host = os.getenv("DB_HOST", "localhost")  
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_name = os.getenv("DB_NAME", "weather_db")
    db_port = os.getenv("DB_PORT", "5432")

    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        engine = create_engine(db_url)
        df.to_sql('weather_logs', engine, if_exists='append', index=False)
        logging.info(f"💾 Successfully committed {len(df)} rows to PostgreSQL.")
    except Exception as e:
        logging.error(f"❌ Database Load Error: {e}")
        print(f"❌ Database Connection Error: {e}")
        raise e  # نرفع الخطأ لكي تلتقطه دالة run_etl_pipeline

# 5. تشغيل الـ Pipeline بالكامل للمدن
def run_etl_pipeline():
    logging.info("⏰ بدء تشغيل الـ Multi-City ETL Pipeline...")
    print(f"⏰ Pipeline started at: {datetime.now()}")
    
    try:
        all_city_dfs = []
        for city_name, coords in CITIES.items():
            raw_data = get_weather_data(city_name, coords['lat'], coords['lon'])
            clean_df = process_data(raw_data, city_name, coords['lat'], coords['lon'])
            if clean_df is not None:
                all_city_dfs.append(clean_df)
                
        if all_city_dfs:
            final_df = pd.concat(all_city_dfs, ignore_index=True)
            
            # حفظ البيانات الخام أولاً
            save_to_db(final_df)
            print("🚀 Multi-city data saved to PostgreSQL successfully!")
            
            # 🔥 المكان السحري: تشغيل التحليلات المتقدمة فوراً بعد نجاح الحفظ في الـ DB
            print("📊 Ingestion completed. Triggering advanced analytics calculations...")
            run_advanced_analytics()
            
        else:
            print("❌ Pipeline execution failed for all cities.")
            send_alert("Pipeline failed: No valid data was extracted or processed from API.")
            
    except Exception as e:
        # إذا حصل أي خطأ في أي مرحلة، يرسل تنبيه فوري للتليجرام
        send_alert(str(e))
        logging.error(f"❌ Critical Pipeline Failure: {e}")

if __name__ == "__main__":
    run_etl_pipeline()
    print("✨ ETL Task executed successfully and finished.")