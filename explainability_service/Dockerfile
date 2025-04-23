FROM python:3.10-slim

WORKDIR /app

# 1) Install shared deps
COPY ../requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# 2) Copy service code + shared modules
COPY explainability_service/service.py  ./service.py
COPY ../app/            ./app/
COPY ../agents/         ./agents/

# 3) Gunicorn & healthcheck
RUN pip install gunicorn
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:5002/health || exit 1

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "service:app"]
