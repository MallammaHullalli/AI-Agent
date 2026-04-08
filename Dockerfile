FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Hugging Face Spaces runs as user 1000
RUN useradd -m -u 1000 user
USER user

EXPOSE 7860

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--chdir", "web", "app:app"]
