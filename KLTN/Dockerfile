# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Cài dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code
COPY . .

# Cho phép chạy script
RUN chmod +x run.sh

EXPOSE 8000

CMD ["sh", "run.sh"]
