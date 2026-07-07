import pytest
import pandas as pd
import requests
import requests_mock
from src.main import get_weather_data, process_data

# 1. اختبار دالة جلب البيانات (get_weather_data) في حالة النجاح
def test_get_weather_data_success():
    city = 'Cairo'
    lat, lon = 30.0444, 31.2357
    
    # محاكاة رد الـ API (Mocking) عشان م نعتمدش على النت أثناء الاختبار
    mock_response = {
        "hourly": {
            "time": ["2026-06-27T16:00"],
            "temperature_2m": [35.5],
            "relativehumidity_2m": [45],
            "windspeed_10m": [12.2]
        }
    }
    
    url_substring = f"latitude={lat}&longitude={lon}"
    
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, json=mock_response)
        result = get_weather_data(city, lat, lon)
        
        assert result is not None
        assert "hourly" in result
        assert result["hourly"]["temperature_2m"][0] == 35.5

# 2. اختبار دالة جلب البيانات في حالة فشل الـ API (Error Handling Test)
def test_get_weather_data_failure():
    city = 'Cairo'
    lat, lon = 30.0444, 31.2357
    
    with requests_mock.Mocker() as m:
        # محاكاة خطأ 500 من السيرفر
        m.get(requests_mock.ANY, status_code=500)
        result = get_weather_data(city, lat, lon)
        
        # الدالة بتاعتنا متأمنة بـ try-except ولازم ترجع None لو حصل خطأ
        assert result is None

# 3. اختبار دالة معالجة وتحويل البيانات (process_data)
def test_process_data_transformation():
    # بيانات خام افتراضية كأنها جاية من الـ API
    raw_json = {
        "hourly": {
            "time": ["2026-06-27T16:00"],
            "temperature_2m": [30.0],
            "relativehumidity_2m": [50],
            "windspeed_10m": [15.0]
        }
    }
    city = 'Alexandria'
    lat, lon = 31.2001, 29.9187
    
    # تشغيل الدالة
    df = process_data(raw_json, city, lat, lon)
    
    # التأكد من صحة الـ Transformation والـ Metadata أوتوماتيكياً
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) == 1
    assert list(df.columns) == ['timestamp', 'temperature', 'humidity', 'wind_speed', 'city', 'latitude', 'longitude', 'created_at']
    assert df['city'].iloc[0] == 'Alexandria'
    assert df['temperature'].iloc[0] == 30.0

    # 4. اختبار قدرة الـ Pipeline على كشف وفلترة البيانات غير المنطقية (Validation Test)
def test_process_data_validation_drops_bad_rows():
    # محاكاة رد API يحتوي على صفوف سليمة وصفات مستحيلة (حرارة 100 ورطوبة بالسالب)
    anomalous_json = {
        "hourly": {
            "time": ["2026-06-28T12:00", "2026-06-28T13:00", "2026-06-28T14:00"],
            "temperature_2m": [32.0, 100.0, 28.5],  # الـ 100 غير منطقية
            "relativehumidity_2m": [55, 40, -15],   # الـ -15 مستحيلة
            "windspeed_10m": [10.0, 12.0, 14.0]
        }
    }
    
    # تشغيل الدالة
    df = process_data(anomalous_json, 'Cairo', 30.0444, 31.2357)
    
    # التأكد من أن الـ Pipeline استبعد الصفوف التالفة واحتفظ فقط بالصف الأول السليم
    assert df is not None
    assert len(df) == 1  # كانو 3 صفوف، لازم يتبقى 1 فقط سليم
    assert 100.0 not in df['temperature'].values
    assert -15 not in df['humidity'].values