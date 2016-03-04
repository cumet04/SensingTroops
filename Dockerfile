FROM python:latest

RUN mkdir -p /opt/app
WORKDIR /opt/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y nodejs nodejs-legacy
RUN wget http://www.npmjs.org/install.sh --no-check-certificate && sh install.sh
RUN npm install -g jasmine-node && npm install frisby
