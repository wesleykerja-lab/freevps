FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home --uid 10001 cscms
COPY backend ./backend
COPY web ./web
COPY docs ./docs
COPY manage.py ./manage.py
RUN mkdir -p /app/data && chown cscms:cscms /app/data
USER cscms
EXPOSE 8000
CMD ["uvicorn","backend.main:app","--host","0.0.0.0","--port","8000","--proxy-headers","--forwarded-allow-ips","*"]
