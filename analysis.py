import os
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

def run_advanced_analytics():
    # 1. الاتصال الآمن بقاعدة البيانات
    DB_HOST = os.getenv("DB_HOST", "db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME = os.getenv("DB_NAME", "weather_db")
    DB_PORT = os.getenv("DB_PORT", "5432")
    
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    try:
        # 2. سحب البيانات الخام
        df = pd.read_sql("SELECT * FROM weather_data", engine)
        if df.empty:
            print("No data found to analyze.")
            return
            
        # تحويل التاريخ لـ datetime لضمان دقة الحسابات التاريخية
        df['dt'] = pd.to_datetime(df['dt'])
        df['week_number'] = df['dt'].dt.isocalendar().week
        
        # 3. العمليات المتقدمة (المتوسط الأسبوعي وأعلى رطوبة لكل مدينة)
        analytics_df = df.groupby(['city', 'week_number']).agg(
            avg_temp=('temp', 'mean'),
            max_humidity=('humidity', 'max'),
            last_updated=('dt', 'max')
        ).reset_index()
        
        # إضافة طابع زمني لوقت الحساب
        analytics_df['calculated_at'] = datetime.now()
        
        # 4. تخزين النتائج في جدول الـ Data Mart (weather_analytics)
        analytics_df.to_sql("weather_analytics", engine, if_exists="replace", index=False)
        print("Advanced analytics calculated and saved to weather_analytics table successfully! 📊")
        
    except Exception as e:
        print(f"Error during analytics processing: {e}")
        raise e

if __name__ == "__main__":
    run_advanced_analytics()