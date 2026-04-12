FROM python:3.11-slim

WORKDIR /booking_service

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. booking.proto

ENV APP_HOST=0.0.0.0
ENV APP_PORT=9090

EXPOSE 9090

CMD ["python", "server.py"]
