FROM python:3.10-slim
WORKDIR /app
COPY ../requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

COPY dashboard_service/service.py ./service.py
EXPOSE 8080
CMD ["python","service.py"]
