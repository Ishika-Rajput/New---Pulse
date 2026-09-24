FROM python:3.12-slim

# Install Node.js
RUN apt-get update \
    && apt-get install -y curl ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY scraper/requirements.txt ./scraper/requirements.txt

RUN pip install --no-cache-dir -r ./scraper/requirements.txt

# Install backend dependencies
COPY backend/package*.json ./backend/

WORKDIR /app/backend

RUN npm ci

# Copy application code
WORKDIR /app

COPY backend ./backend
COPY scraper ./scraper

# Backend port
EXPOSE 5000

WORKDIR /app/backend

CMD ["npm", "start"]