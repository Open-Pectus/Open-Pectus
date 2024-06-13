
# Error Recovery - Detailed design

# 1. Content
- [Error Recovery - Detailed design](#error-recovery---detailed-design)
- [1. Content](#1-content)
- [2. Hardware errors](#2-hardware-errors)
  - [2.1 TODO. Mainly just move the description from \\engine\\hardware\_error.py to here.](#21-todo-mainly-just-move-the-description-from-enginehardware_errorpy-to-here)
- [3. Protocol errors](#3-protocol-errors)
  - [3.1 Overview](#31-overview)
  - [3.2 Engine](#32-engine)
  - [3.3 Aggregator](#33-aggregator)


# 2. Hardware errors
This chapter describes how hardware connection errors are handled and detailed design of the implementation.

## 2.1 TODO. Mainly just move the description from \engine\hardware_error.py to here.


# 3. Protocol errors
This chapter describes the handling of errors in the Engine-Aggregator connection and detailed design of the implementation.

## 3.1 Overview
The overall aim is to ensure that both Aggregator and Engine are rescilient to temporary connection errors. If the network is down 
during a run and then comes back up later, both Aggregator and Engine should be able to recover from this such that:
1. When the connection is lost
    - Engine begins batching up samples of the data that can not be sent to Aggregator
      - If a run is active, engine keeps running the method
      - If no run is active, probably does nothing
    - Aggregator notices that the Engine is unavailable and reports this status to the front end
      - Frontend should somehow display this state, similar to the "Interrupted by error" state
        - Commands cannot be sent to Engine
2. When the connection is recovered
    - Engine sends the batched up values
    - Aggregator notices that Engine is available and reports this status to the front end
      - If the run is still active, continue as if nothing happened
      - If run is failed or completed, update the persisted state to reflect this, same as if it was connected when it happened
  

## 3.2 Engine
Error handling is added to engine_dispatcher which can detect connection errors and sample and batch up messages. When connection is reestablished,
data can be sent. Engine does not know or need to know about errors (?).

This can be implemented as a decorator around EngineDispatcher and be completely transparent towards Engine (clients of EngineDispatcher). For this
to work the low level connection handling must be autonomous and self-healing. This should be the case with WebSocketRpcClient already, but it
must be verified and tested. In particular, we need more protocol tests to which these tests can be added.

To make the dispatchers testable, base classes are introduced that contain non-network details. These are subclassed in production versions
using rest/websockets and in test versions using direct connection.

TODO: Once decoupled, create tests that verify the protocol behavior. These can the be extended later on to verify error handling


## 3.3 Aggregator

