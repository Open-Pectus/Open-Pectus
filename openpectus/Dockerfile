FROM python:3.13-alpine

# Install openpectus and dependencies
WORKDIR /usr/src/app
RUN mkdir -p /data
COPY dist ./dist/
RUN pip install --no-cache-dir dist/openpectus.tar.gz

ENV AGGREGATOR_PORT=8300
EXPOSE $AGGREGATOR_PORT

CMD pectus-aggregator --host 0.0.0.0 --port $AGGREGATOR_PORT --database /data/open_pectus_aggregator.sqlite3
