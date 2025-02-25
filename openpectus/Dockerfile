FROM python:3.13

# see https://hub.docker.com/_/python/

WORKDIR /usr/src/app
RUN mkdir -p /data
COPY dist ./dist/
RUN pip install --no-cache-dir dist/openpectus.tar.gz

# LSP port
EXPOSE 2087

ENV AGGREGATOR_PORT=8300
EXPOSE $AGGREGATOR_PORT

CMD pectus-aggregator --host 0.0.0.0 --port $AGGREGATOR_PORT --database /data/open_pectus_aggregator.sqlite3 --lsp
