import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression # أو نقدر نستخدم PyTorch لعمل RNN/LSTM لاحقاً
from datetime import datetime, timedelta

def train_weather_predictor():
    # 1. الاتصال بقاعدة البيانات
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME = os.getenv("DB_NAME", "weather_db")
    DB_PORT = os.getenv("DB_PORT", "5432")
    
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    try:
        # 2. سحب البيانات التاريخية من الجدول السليم
        df = pd.read_sql("SELECT timestamp, temperature, humidity, wind_speed FROM weather_logs", engine)
        if len(df) < 24: # محتاجين على الأقل بيانات يوم كامل عشان نبدأ
            print("Not enough data to train the ML model yet. Gathering more logs... 📊")
            return
            
        # 3. تجهيز الميزات (Feature Engineering)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_year'] = df['timestamp'].dt.dayofyear
        
        # هنخلي الموديل يتنبأ بدرجة الحرارة بناءً على الساعة واليوم في السنة والرطوبة الحالية
        X = df[['hour', 'day_of_year', 'humidity', 'wind_speed']]
        y = df['temperature']
        
        # 4. تدريب الموديل
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_test_split=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        print(f"🎯 ML Model trained successfully! Score: {model.score(X_test, y_test):.2f}")
        
        # 5. عمل توقع للساعة القادمة كمثال وتخزينه
        # (تقدري تعرضي التوقع ده جوه الـ Streamlit Dashboard بتاعتك!)
        
    except Exception as e:
        print(f"ML Training Error: {e}")

if __name__ == "__main__":
    train_weather_predictor()