# ==============================================================================
# Overleaf LaTeX Engine - Dockerfile
# Full Open-Source Python LaTeX to PDF Compiler & Real-time Web IDE
# ==============================================================================

FROM python:3.12-slim-bookworm

# Prevent Python from writing .pyc files & enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000

# Install required system tools, SSL certificates, fonts and libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    tar \
    gzip \
    fontconfig \
    libfontconfig1 \
    libfreetype6 \
    libgraphite2-3 \
    libharfbuzz0b \
    libicu72 \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Install Standalone Static Tectonic LaTeX Compiler Binary (x86_64 / musl)
ARG TECTONIC_VERSION=0.15.0
RUN curl -fsSL "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%40${TECTONIC_VERSION}/tectonic-${TECTONIC_VERSION}-x86_64-unknown-linux-musl.tar.gz" -o /tmp/tectonic.tar.gz \
    && tar -xzf /tmp/tectonic.tar.gz -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/tectonic \
    && rm /tmp/tectonic.tar.gz \
    && tectonic --version

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./app/
COPY README.md .

# Create persistent data directories
RUN mkdir -p data/workspaces data/bin

# Expose Web IDE Port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/login || exit 1

# Start FastAPI application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
