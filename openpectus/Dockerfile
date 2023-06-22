FROM python:3

# see https://hub.docker.com/_/python/

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install .\dist\OpenPectus-0.0.1.tar.gz

COPY . .
WORKDIR /usr/src/app/aggregator

EXP0OSE 8300
CMD python3 -m uvicorn main:app --host 0.0.0.0 --port 8300
