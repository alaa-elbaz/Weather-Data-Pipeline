# 1. استخدام نسخة خفيفة ومستقرة من بايثون كقاعدة
FROM python:3.10-slim

# 2. تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# 3. تثبيت الأدوات الأساسية للنظام لضمان عمل psycopg2 بدون مشاكل
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. نسخ ملف المكتبات أولاً للاستفادة من الـ Caching في دوكر
COPY requirements.txt .

# 5. تثبيت مكتبات البايثون
RUN pip install --no-cache-dir -r requirements.txt

# 6. نسخ باقي ملفات المشروع إلى داخل الحاوية
COPY . .

# 7. فتح المنفذ الخاص بـ Streamlit (الافتراضي هو 8501)
EXPOSE 8501

# 8. الأمر النهائي لتشغيل الـ Dashboard فور تشغيل الحاوية
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]