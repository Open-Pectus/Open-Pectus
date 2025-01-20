.. role:: console(code)
   :language: console
.. role:: python(code)
   :language: python

.. _error_recovery:

Error Recovery
==============
This chapter describes how hardware connection errors are handled and detailed design of the implementation.

.. contents:: Table of Contents
  :local:
  :depth: 3

Handling of Hardware Connection Errors
--------------------------------------
Error recovery has the 5 states defined in :console:`ErrorRecoveryState`: Disconnected, OK, Issue, Reconnect or Error. It is configured using the time thresholds defined in :console:`ErrorRecoveryConfig`.

Once an engine is connected to hardware I/O, state is :console:`OK`. This state is kept until a read or write error occurs. Such an error causes state to transition to :console:`Issue`.
In this state, if a success read/write occurs, state transitions back to :console:`OK`. If no success read/write occurs within a duration of :console:`issue_timeout_seconds`, state is set to :console:`Reconnect`.

In state :console:`Reconnect`, reconnect attempts are started. If successful, state is set to :console:`OK`. If not successful within a duration of `error_timeout_seconds`, state is set to :console:`Error`.

While in states `Issue` and `Reconnect`, any read and write errors are masked by returning last-known-good values for reads and caching values for writes. This means that the engine (and the user) will not notice the connection loss immediately.

The one exception to this is UOD commands. We have to assume that a UOD command cannot execute correctly without hardware connection so we have to fail UOD commands. (A possible improvement would be to require UOD commands to consider the connection and fail with predefined exception types).

In state :console:`Error`, reconnect attempts continue but errors are no longer masked. The :console:`Connection Status` tag is set to :console:`Disconnected`. If reconnect is successful, state is set to :console:`OK` and :console:Connection Status` is set to :console:`Connected`.

The consequence of no longer masking errors, is that the Engine will enter the `paused on error` state where the user can decide whether to continue or not.

.. note::
   It is unlikely but possible that errors occur so soon after successful connection that no value is yet available as last-known-good. In this case, a read returns a None value and the error is logged.


Implementation
^^^^^^^^^^^^^^
Error recovery is implemented using a decorator pattern around the :python:`HardwareLayerBase` hardware abstraction class. The class :python:`ErrorRecoveryDecorator` implements the :python:`HardwareLayerBase` interface by wrapping the concrete :python:`HardwareLayerBase` class, e.g.
:python:`OPCUA_Hardware` and delegating calls to it. However, when the concrete class fails with a connection related error, the decorator masks the read or write error as discussed above.

.. note::
    The implementation uses the tick() method to detect and execute reconnect. If this takes too long and hurts engine timing, the hardware should instead implement its reconnect via threading.


Handling of Engine/Aggregator Protocol Errors
---------------------------------------------
This section describes the handling of errors in the Engine-Aggregator connection and detailed design of the implementation.

The overall aim is to ensure that both Aggregator and Engine are resilient to temporary connection errors. If the network is down during a run and then comes back up later, both Aggregator and Engine should be able to recover from this such that:

#. When the connection is lost

   - Engine creates a `ReconnectedMsg` that contains a snapshot of its state at the time of the disconnect
   - Engine begins buffering up samples of the data that can not be sent to Aggregator

     - If a run is active, engine keeps running the method

   - Aggregator notices that the Engine is unavailable and reports this status to the front end

     - Frontend should somehow display this state, similar to the "Interrupted by error" state
     - Commands cannot be sent to Engine
#. When the connection is recovered

   - Engine sends the `ReconnectedMsg` created earlier
   - Engine sends the buffered up values
   - Aggregator notices that Engine is available and reports this status to the front end
   - Aggregator processes the `ReconnectedMsg` to restore its `engine_data` state for the engine at the time of the disconnect.

     - If the run is still active, continue the run
     - If run is failed or completed, update the persisted state to reflect this, same as if it was connected when it happened

#. Aggregator restart must be supported such that

   - Any connected engines reconnect when aggregator comes back up
   - Aggregator detects whether engines are in an active run or have completed a run and stores the correct information


Engine
------
Error handling is implemented which can detect connection errors, sample and batch up data messages. When connection is reestablished, data can be sent.

It is implemented in the :python:`EngineRunner` class which uses :python:`EngineDispatcher` to implement an autonomous and self-healing connection (at least when the connection is recovered in reasonable time).

To make the dispatchers testable, base classes are introduced that contain non-network details. These are subclassed in production versions using REST/WebSockets and in test versions using direct connection.

Aggregator
----------
To make the aggregator resilient towards connection errors, little is needed. When an engine is disconnected, the WebSocket :python:`on_disconnect` callback fires and the data for en engine is removed. Additionally, the engine data is saved as a :python:`RecentEngine`.


Sequences
---------
..
   Mermaid syntax: https://emersonbottero.github.io/mermaid-docs/syntax/sequenceDiagram.html

Connect Sequence
^^^^^^^^^^^^^^^^
When engine starts, it starts the Connect sequence.

.. mermaid::
    :caption: Engine connect sequence.
    :align: center

    sequenceDiagram
       participant E as Engine
       participant A as Aggregator

       Note over E, A: Connect sequence
       E ->> A: register (post)
       activate E
       activate A
       A -->> E: engine_id
       deactivate A
       E ->> A: connect (websocket)

       activate A
       A ->> E: get_engine_id_async
       E -->> A: engine_id
       A ->> A: verify engine_id
       A -->> E: accept websocket connection
       deactivate A  

       Note over E, A: Connection error
       E ->> E: raise ProtocolNetworkException

       deactivate E


Steady-State Sequence
^^^^^^^^^^^^^^^^^^^^^
When the Connect sequence has executed successfully, the Steady-State sequence is activated.

.. mermaid::
    :caption: Engine steady-state sequence.
    :align: center

    sequenceDiagram
       participant E as Engine
       participant A as Aggregator

       Note over E, A: Steady-State sequence
       activate E
       loop every 0.5 second
          E ->> A: control messages (websocket)
       end
       loop every second
          E ->> A: data messages (websocket)
       end

       alt user command
          A ->> E: command (websocket)
          activate A
          E -->> A: response
          deactivate A
       end

       Note over E, A: Network error
       E ->> E: raise ProtocolNetworkException

       deactivate E


Reconnect Sequence
^^^^^^^^^^^^^^^^^^
When a ProtocolNetworkException is encountered in either the Connect sequence or the Steady-State sequence, the error recovery mechanism switches to the Reconnect sequence.

The Reconnect sequence is just the Connect sequence followed by:

* A single ReconnectEngMsg (which allows the aggregator to restore its state for the particular engine)
* A number of data and control messages that were buffered up while the Engine was disconnected

If a network error occurs, the sequence is reset and started again.

When the Reconnect sequence (including Catch-up) is complete, the Steady-State sequence is activated.

.. mermaid::
    :caption: Engine reconnect sequence.
    :align: center

    sequenceDiagram
       participant E as Engine
       participant A as Aggregator

       Note over E, A: Reconnect sequence
       E ->> A: register (post)
       activate E
       activate A
       A -->> E: engine_id
       deactivate A
       E ->> A: connect (websocket)

       activate A
       A ->> E: get_engine_id_async
       E -->> A: engine_id
       A -->> E: accept websocket connection
       deactivate A

       Note over E, A: Catch-up
       E ->> A: reconnect message
       activate A
       A ->> A: reestablish session
       loop Send buffered messages
          E --> A: buffered message
       end
       deactivate A

       Note over E, A: Network error
       E ->> E: raise ProtocolNetworkException
       deactivate E


Recovery States
---------------
These are the system states of connection recovery in the Aggregator-Engine protocol.
It is implemented in the :python:`engine.engine_runner` module.

.. mermaid::
    :caption: Engine recovery states.
    :align: center

    stateDiagram-v2
       Started --> Connected
       Started --> Failed
       Connected --> Failed
       Failed --> Disconnected
       Disconnected --> Reconnecting
       Disconnected --> Failed
       Reconnecting --> CatchingUp
       Reconnecting --> Failed
       CatchingUp --> Reconnected
       CatchingUp --> Failed
       Reconnected --> Failed

