FROM python:3.13-alpine AS base

# Install openpectus and dependencies
WORKDIR /usr/src/app
RUN mkdir -p /data
RUN mkdir -p /webpush_keys
COPY dist ./dist/
RUN pip install --no-cache-dir dist/openpectus.tar.gz
RUN rm -R ./dist

# Squash layers to reduce image size
FROM scratch
COPY --from=base / /

ENV AGGREGATOR_PORT=8300
EXPOSE $AGGREGATOR_PORT

CMD pectus-aggregator --host 0.0.0.0 --port $AGGREGATOR_PORT --database /data/open_pectus_aggregator.sqlite3 --webpush_keys_path /webpush_keys
