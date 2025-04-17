FROM python:3.10-slim

WORKDIR /app

# 1) Copy shared requirements first so they can cache
COPY ../requirements.txt ./requirements.txt

# 2) Install all shared deps
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

RUN echo "💥 Building the real Dockerfile at $(date)"

RUN apt-get update \
 && apt-get install -y curl \
 && rm -rf /var/lib/apt/lists/*

# 3) Copy only what this microservice needs
COPY novelty_service/service.py       ./service.py
COPY ../app/        ./app/
COPY ../agents/     ./agents/

# 4) Health check
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:5050/health || exit 1

RUN pip install gunicorn

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5050", "service:app"]
  
