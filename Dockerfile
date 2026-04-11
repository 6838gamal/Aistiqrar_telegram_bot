FROM python:3.11-slim

WORKDIR /app

# منع مشاكل بعض المكتبات
ENV PYTHONUNBUFFERED=1

# تثبيت dependencies النظامية (مهم لـ aiohttp أحيانًا)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# نسخ الملفات
COPY requirements.txt .

# تثبيت بايثون مكتبات
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# تشغيل البوت + FastAPI
CMD ["python", "run.py"]
