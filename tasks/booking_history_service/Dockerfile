FROM python:3.11-slim

WORKDIR /booking_history_service

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
