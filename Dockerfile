FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Hugging Face Spaces use port 7860 by default
EXPOSE 7860

# Run the Streamlit dashboard
CMD ["streamlit", "run", "dashboard.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
