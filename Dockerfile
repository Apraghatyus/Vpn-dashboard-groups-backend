# ═══════════════════════════════════════════════
# WG-ACL Manager — Backend (Flask)
# Placeholder — se completará después
# ═══════════════════════════════════════════════

FROM python:3.12-slim

WORKDIR /app

# Dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Directorio de datos
RUN mkdir -p /app/data

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
