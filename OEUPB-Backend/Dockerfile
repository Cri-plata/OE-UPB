FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN addgroup --system oeupb && adduser --system --ingroup oeupb oeupb
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER oeupb
EXPOSE 8000
# El backend solo es accesible desde el proxy en la red interna de Compose (no publica puertos):
# se confía en sus cabeceras X-Forwarded-* para que las URL generadas usen https.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*", "--no-access-log"]
