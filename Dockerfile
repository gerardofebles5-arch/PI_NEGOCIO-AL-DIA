# ---------- Stage 1: build the frontend ----------
FROM node:20-slim AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---------- Stage 2: backend + static ----------
FROM python:3.12-slim AS runtime
WORKDIR /app

# System deps: Tesseract (OCR, español + inglés) for images and scanned PDFs.
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
# Built SPA served by FastAPI from backend/static.
COPY --from=frontend /frontend/dist ./static

ENV DATABASE_URL=sqlite:////app/data/pinad.db \
    UPLOAD_DIR=/app/data/uploads \
    PORT=8000

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
