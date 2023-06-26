FROM python:3

# see https://hub.docker.com/_/python/

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY dist ./dist/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install dist/openpectus-0.0.1.tar.gz

WORKDIR /usr/src/app/aggregator

EXPOSE 8300
#CMD python3 -m uvicorn main:app --host 0.0.0.0 --port 8300
CMD python3 main.py --host 0.0.0.0 --port 8300
