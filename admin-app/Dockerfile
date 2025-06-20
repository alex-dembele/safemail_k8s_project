FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# La création de l'admin se fera manuellement via 'kubectl exec'
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "app:create_app()"]
