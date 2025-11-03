FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies and jq for JSON parsing
RUN apt-get update && apt-get install -y wget unzip curl jq gnupg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome and matching Chromedriver
RUN set -ex \
    && CHROME_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json | jq -r '.channels.Stable.version') \
    && echo "Installing Chrome ${CHROME_VERSION}" \
    && wget -t 3 -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip" -O /tmp/chrome.zip \
    && wget -t 3 -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chrome.zip -d /opt/ \
    && unzip /tmp/chromedriver.zip -d /opt/ \
    && mv /opt/chrome-linux64 /opt/chrome \
    && mv /opt/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/*.zip

# Set Chrome environment variables
ENV CHROME_BIN=/opt/chrome/chrome
ENV PATH="/usr/local/bin:/opt/chrome:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose Render port
EXPOSE 8080

# Start Flask app with Gunicorn (Render uses $PORT)
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:${PORT}"]
# Expose port
EXPOSE 9936

# Run app with gunicorn
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:9936"]
EXPOSE 5000
CMD gunicorn main:app --bind 0.0.0.0:$PORT
