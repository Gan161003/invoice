# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy files
COPY . .

# Streamlit config
RUN mkdir -p /root/.streamlit

RUN echo "\
[server]\n\
port = 8501\n\
address = '0.0.0.0'\n\
headless = true\n\
" > /root/.streamlit/config.toml

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
