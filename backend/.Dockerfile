FROM python:3.12.4
WORKDIR /backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /backend/
EXPOSE 8000
