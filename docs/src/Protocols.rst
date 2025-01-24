.. role:: console(code)
   :language: console

Protocols
=========
Open Pectus comprises of 3 major components: Engine, Aggregator and Frontend. The protocols that connect them are described in the following.

.. contents:: Table of Contents
  :local:
  :depth: 3

Frontend/Aggregator Protocol
----------------------------
The frontend/aggregator protocol is primarily REST-based, but includes push messages via WebSocket.

REST
^^^^
The REST protocol contains these interactions:

.. mermaid:: mermaid/frontend_aggregator_rest_interactions.mdd
   :caption: Frontend/Aggregator REST interactions.
   :align: center

WebSocket
^^^^^^^^^
The WebSocket interactions are all push messages that instruct the frontend to
request updates of a certain kind.

The available messages are:

* :console:`RUN_LOG`
* :console:`METHOD`
* :console:`CONTROL_STATE`
* :console:`ERROR_LOG`
* :console:`PROCESS_UNITS`

The frontend knows the relevant REST endpoints that correspond to each type of message.

.. mermaid:: mermaid/frontend_aggregator_websocket_interactions.mdd
   :caption: Frontend/Aggregator WebSocket interactions.
   :align: center

Engine/Aggregator Protocol
--------------------------
The engine/aggregator protocol is primarily WebSocket-based, but includes REST messages for registration and health check.

This protocol ensures that the aggregator is kept updated on engines (process units) and their states.
It also allows users of the frontend to control connected engines.

.. note::
   This diagram shows a simplified overview. The actual protocol is more elaborate due to its built-in error recovery. This allows it to support temporarily disconnected engines as well as updating and/or restarting the aggregator during active runs. This is documented in :ref:`error_recovery`.

.. mermaid:: mermaid/engine_aggregator_protocol_overview.mdd
   :caption: Engine/Aggregator protocol overview.
   :align: center

State Diagrams
--------------
This section documents the important states and state changes in openpectus.

.. note::
   Note on transition naming:
   
   # Lower case transitions (e.g. "register ok") denote some action in the system.
   # Capitalized transitions (e.g. "Start") denote a specific command being executed.

Engine States
^^^^^^^^^^^^^
When an engine is started, it automatically connects to the hardware specified in its UOD and to the aggregator URL specified as command line argument. It cannot function properly if either of these connections are unavailable on startup (though the error recovery features will continuously attempt to recover).

Once both connections are in place, the engine is in state :console:`Connected`. This means that:

# Engine is ready to receive commands or run a method.
# The scan cycle loop is started so tag values are continuously read from hardware
# Engine is displayed in the frontend dashboard as a process unit with status :console:`Ready` 
# Engine details can be viewed in frontend details, including real-time updated values of its configured tags.

This state is also referred to as :console:`Steady State` (as opposed to states such as :console:`starting/initializing/connecting/reconnecting`).

Avoid using the term `Running` the describe Engine state because is ambiguous. It might mean that the engine is *Connected*/in *Steady State*, or it could mean that a method is running. The term `Connected` is used here and in the diagrams to refer to an engine in Steady State.

.. mermaid:: mermaid/engine_state_diagram.mdd
   :caption: Engine state diagram.
   :align: center

Aggregator States
^^^^^^^^^^^^^^^^^
The aggregator manages a number of engines and tracks the state of each one.

.. note::
   Persistence of run state is based changes on the :console:`run_id` system tag. If no longer set, all collected data is saved as a complete run.

.. mermaid:: mermaid/aggregator_state_diagram.mdd
   :caption: Aggregator state diagram.
   :align: center

Deployment Diagram
^^^^^^^^^^^^^^^^^^

.. mermaid:: mermaid/c4_deployment_diagram.mdd
   :caption: Deployment diagram.
   :align: center

.. _csv_file_format:

CSV File Format
---------------

It is possible to export data from a concluded run to a CSV file.
The CSV file includes metadata and time series data for all tags defined in the :ref:`unit_operation_definition`. An example of a CSV file generated for a run using the built-in :console:`demo_uod.py` UOD is given in :numref:`csv_example`.

A download link is available in the frontend user interface. It is also possible to download the CSV file using the :ref:`openapi_specification` :console:`/api/recent_runs/{run_id}/csv_file` endpoint.

.. _csv_example:
.. code-block:: python
   :caption: Example of exported CSV file. Filename: :console:`RecentRun-c87d65e2-7e1a-4477-aa89-b4f56db75773.csv`

   # Recent Run Id,c87d65e2-7e1a-4477-aa89-b4f56db75773
   # Engine Id,LC...50_DemoUod
   # Engine Computer name,LC...50
   # Engine Version,0.1.13
   # Engine Hardware tring,"ErrorRecoveryDecorator(state=ErrorRecoveryState.OK,decorated=DemoHardware)"
   # Uod author nam,Demo Author
   # Uod author email,demo@openpectus.org
   # Uod file name,C:\Users\...\openpectus/engine/configuration/demo_uod.py
   # Aggregator Computer name,AZR-PECTUS-PRD
   # Aggregator Version,0.1.13
   # Starting Time (UTC),2025-01-09 20:15:02.926612
   # Ending Time (UTC),2025-01-09 20:16:07.110109
   # Contributors,E..L

   Run Time [s],FT01 [L/h],TestInt,TestFloat [kg],TestString,Category,FT02 [L/h],Time [s],Reset,System State,CmdWithRegexArgs [dm2],TestPercentage [%]
   0.0,10,42,9.87,test,Rising,10.795927561732627,2.3903110027313232,N/A,Stopped,34.87,34.87
   5.34400000000096,12,42,9.87,test,Rising,12.552170854700819,7.742166519165039,N/A,Stopped,34.87,34.87

.. _openapi_specification:

OpenAPI
-------

The OpenAPI specification is listed below. It is also available at the :console:`/docs` endpoint on the Aggregator e.g. :console:`http://localhost:9800/docs`.

.. openapi:: openapi.yml
   :examples: