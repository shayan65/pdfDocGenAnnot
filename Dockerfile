
# For more information, please refer to https://aka.ms/vscode-docker-python
# FROM python:3.8-slim
# FROM ubuntu:18.04
FROM pachyderm/opencv
LABEL mantainer="shayan hemmatiyan <shayan hemmatiyan@gmail.com"
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update -y \
    && apt install libgl1-mesa-glx -y \
    && apt-get install 'ffmpeg' 'libsm6' 'libxext6' poppler-utils libgl1-mesa-dev -y

RUN pip install --upgrade pip

WORKDIR /pdfdocgen

COPY requirements.txt .

RUN pip install setuptools==59.5.0 wheel

RUN  pip install -r requirements.txt

COPY . .

EXPOSE 2222 8080


CMD python app.py