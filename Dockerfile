FROM python:3.10-slim

WORKDIR /app

# نسخ ملف المتطلبات أولاً للاستفادة من الـ Caching
COPY requirements.txt .

# تثبيت مكتبات بايثون مباشرة (الآن psycopg2-binary لن تحتاج لأدوات نظام)
RUN pip install --no-cache-dir -r requirements.txt

# نسخ بقية ملفات المشروع
COPY . .

# تشغيل التطبيق (أو الأمر الافتراضي الذي يعوضه الـ docker-compose)
CMD ["python", "main.py"]