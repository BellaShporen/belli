FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY proxy.crt /usr/local/share/ca-certificates/proxy.crt
RUN update-ca-certificates

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY slack_connections.py .

CMD ["python", "slack_connections.py"]
