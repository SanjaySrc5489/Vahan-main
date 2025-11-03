FROM python:3.10-slim

# Install dependencies for Chrome + Selenium
RUN apt-get update && apt-get install -y wget curl gnupg unzip fonts-liberation libxss1 libappindicator3-1 libatk-bridge2.0-0 libgtk-3-0 libnss3 libx11-xcb1 xvfb \
    && mkdir -p /usr/share/desktop-directories

# Add Google Chrome repo and install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-signing-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install the latest Chromedriver (always works)
RUN DRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV DISPLAY=:99

EXPOSE 9936
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:9936"]
