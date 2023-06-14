FROM python:3

# see https://hub.docker.com/_/python/

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8300
CMD python3 -m uvicorn main:app --host 0.0.0.0 --port 8300
