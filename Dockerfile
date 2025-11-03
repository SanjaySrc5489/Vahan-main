# Use Python base
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome (official testing version) + matching driver
RUN CHROME_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json | grep -oP '(?<="Stable": \{"version": ")[^"]*') \
    && echo "Installing Chrome ${CHROME_VERSION}" \
    && wget -q https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip -O /tmp/chrome.zip \
    && wget -q https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip -O /tmp/chromedriver.zip \
    && unzip /tmp/chrome.zip -d /opt/ \
    && unzip /tmp/chromedriver.zip -d /opt/ \
    && mv /opt/chrome-linux64 /opt/chrome \
    && mv /opt/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/*.zip

# Environment variables
ENV CHROME_BIN=/opt/chrome/chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV PATH="/usr/local/bin:/opt/chrome:${PATH}"

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port for Render
EXPOSE 5000
CMD gunicorn main:app --bind 0.0.0.0:$PORT
