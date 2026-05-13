# import urllib.request
# import json
# from datetime import datetime

# def get_weather_data():
#     # إحداثيات القاهرة 
#     lat, lon = 30.0444, 31.2357
    
#     url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relativehumidity_2m,windspeed_10m&timezone=Africa/Cairo"
    
#     try:
#         with urllib.request.urlopen(url) as response:
#             if response.status != 200:
#                 raise Exception(f"HTTP status {response.status}")
#             data = json.load(response)
#         print("✅ Data fetched successfully!")
#         return data
#     except Exception as e:
#         print(f"❌ Error fetching data: {e}")
#         return None

# if __name__ == "__main__":
#     raw_data = get_weather_data()
#     if raw_data:
#         # عرض أول 5 سجلات فقط 
#         print(raw_data['hourly']['time'][:5])




import requests
import pandas as pd
import os
import logging
from sqlalchemy import create_engine
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# إعداد نظام التسجيل (Logging)
logging.basicConfig(
    filename='pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# داخل الدوال، بدلاً من print استخدمي logging.info
def get_weather_data():
    logging.info("بدء عملية سحب البيانات...")
    # ... الكود السابق ...
    logging.info("تم سحب البيانات بنجاح ✅")

    
def save_to_db(df):
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@localhost:5432/{os.getenv('DB_NAME')}"
    
    try:
        engine = create_engine(db_url)
        
        table_name = 'weather_logs'
        
        #  إرسال البيانات
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print("🚀 Data saved to PostgreSQL successfully!")
        
    except Exception as e:
        print(f"❌ Database Error: {e}")


def get_weather_data():
    # إحداثيات القاهرة
    lat, lon = 30.0444, 31.2357
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relativehumidity_2m,windspeed_10m&timezone=Africa/Cairo"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def process_data(json_data):
    # 1. استخراج البيانات الساعية
    hourly_data = json_data['hourly']
    
    # 2. تحويل  إلى DataFrame 
    df = pd.DataFrame(hourly_data)
    
    # 3. تحويل عمود الوقت من نصوص إلى  DateTime 
    df['time'] = pd.to_datetime(df['time'])
    
    # 4. إعادة تسمية الأعمدة 
    df.columns = ['timestamp', 'temperature', 'humidity', 'wind_speed']
    
    # 5. إضافة عمود لاسم المدينة (Metadata)
    df['city'] = 'Cairo'
    
    # 6. إضافة عمود يوضح متى تم سحب هذه البيانات (Record Creation Time)
    df['created_at'] = datetime.now()
    
    return df

if __name__ == "__main__":
    raw_data = get_weather_data()
    if raw_data:
        clean_df = process_data(raw_data)
        save_to_db(clean_df) # الخطوة الجديدة

        # عرض شكل البيانات النهائي
        print("\n--- Clean Data Sample ---")
        print(clean_df.head()) # عرض أول 5 سطور
        
        print("\n--- Data Info ---")
        print(clean_df.info()) # عرض أنواع البيانات في كل عمود