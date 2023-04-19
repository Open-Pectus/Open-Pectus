Notes:

# Docker

To start all services in docker, run the following command from the `openpectus` directory:
`docker compose up --build` 

When the container is running, the aggregator services are available, including:
OpenAPI UI: http://localhost:8300/docs
OpenAPI spec: http://localhost:8300/openapi.json


## Flake
Run flake locally:
flake must be run from the proper directory in order to read its configuration. Otherwise it uses default
configuration which outputs many errors that are not relevant.

cd Open-Pectus\openpectus
flake8


# Compoents

## Pectus UI

This is a web application that allows users to view and interact with the Pectus system,
including runnings engines and process unit hardware attached to them.

## Aggregator

There is one Aggregator service in a pectus system. It has the following responsibilities:

- Manage Engine services via a web-socket protocol
- Expose the Pectus UI web client application to end users
- Expose a rest API for Pectus UI
- Expose a web-socket API for Pectus UI. Used for two-way features not feasible in rest API.
- Expose a Language Server Protocol web-socket API for the Pectus UI code editor
- Parse and analyze pectus code (requires no running engine, only knowledge of the UOD)

## Engine

An Engine service instance is required for each piece of process unit hardware. It has 
the following responsibilities:

- Communicate with the hardware
- Expose hardware state as Tags
- Expose hardware interaction as Commands
- Parse(?), analyze(?) and run pectus code

# Protocols


