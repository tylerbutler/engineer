# Python 2.7 environment for legacy engineer static site generator
FROM python:2.7-slim

WORKDIR /app

# Debian Buster is EOL - use archive repositories
RUN sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list

# Install build dependencies for native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy the rest of the application (including .git for version generation)
COPY . .
COPY .git .git

# Install engineer in development mode
RUN pip install -e .

ENTRYPOINT ["engineer"]
