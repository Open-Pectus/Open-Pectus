FROM python:3.11

# see https://hub.docker.com/_/python/

WORKDIR /usr/src/app
RUN mkdir -p /usr/src/app/data
COPY dist ./dist/
RUN pip install --no-cache-dir dist/openpectus.tar.gz

ENV AGGREGATOR_PORT=8300

EXPOSE $AGGREGATOR_PORT
CMD pectus-aggregator --host 0.0.0.0 --port $AGGREGATOR_PORT --database /usr/src/app/data/open_pectus_aggregator.sqlite3
