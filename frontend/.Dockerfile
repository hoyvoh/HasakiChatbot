FROM python:3.12.4-alpine
WORKDIR /frontend
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /frontend/
EXPOSE 8501
