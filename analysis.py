import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

def analyze_weather():
    # الاتصال بالقاعدة
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@localhost:5432/{os.getenv('DB_NAME')}"
    engine = create_engine(db_url)
    
    # قراءة البيانات باستخدام SQL
    query = "SELECT * FROM weather_logs"
    df = pd.read_sql(query, engine)
    
    if not df.empty:
        print("\n📊 --- إحصائيات سريعة للطقس ---")
        print(f"متوسط درجة الحرارة: {df['temperature'].mean():.2f}°C")
        print(f"أعلى سرعة رياح: {df['wind_speed'].max()} km/h")
        print(f"عدد السجلات المخزنة: {len(df)}")
    else:
        print("القاعدة فارغة حالياً.")

if __name__ == "__main__":
    analyze_weather()