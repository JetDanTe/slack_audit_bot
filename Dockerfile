FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY doc/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p logs

COPY app/ .

ENV LOG_LEVEL=INFO
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
