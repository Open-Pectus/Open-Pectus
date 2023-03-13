Welcome to the Open Pectus documentation!
=========================================
Open Pectus is a process control system for Unit Operations such as filtration, chromatography, precipitation, solubilization and refolding. Pectus implements a language called P-code which is used to write methods and control components on the Unit Operation.

OP distinguishes itself as a process control system by giving the user access to and control of the machine code that is executed. The user is free to write P-code by hand but the intention is also that P-code can be generated with high-level wizards. P-codes are executed "live" and even a running method can be changed and extended.

Architecture
------------
On a high level, Open Pectus consists of three separate parts:

#. Engine which executes commands and methods and interacts with the Unit Operation I/O for a single Unit Operation. The Engine connects with the Aggregator.
#. Aggregator facilitates communication between end users and engines.
#. Web frontend user interface

The arcietecture is sketched in :numref:`open-pectus-architecture`. 

.. _open-pectus-architecture:
.. mermaid::
    :caption: Open Pectus architecture.
    :align: center
    
    graph LR
        X[End user 1]--> A
        X --> |WebSockets| B
        Y[End user 2]--> A
        Y --> |WebSockets| B
        Z[End user 3]--> A
        Z --> |WebSockets| B
        subgraph vm[<b>Virtual machine</b>]
            A[Web frontend] 
            B[Aggregator]
        end
        subgraph uo3[<b>Computer at site B</b>]
            B <--> |WebSockets Engine API| E[Engine i]
            E <--> |OPC-UA| H[Unit Operation i]
        end
        subgraph uo1[<b>Computer at site A</b>]
            B <-->|WebSockets Engine API| C[Engine 1]
            C <--> |OPC-UA| F[Unit Operation 1]
            B <-->|WebSockets Engine API| D[Engine 2]
            D <--> |OPC-UA| G[Unit Operation 2]
        end

End User
^^^^^^^^
The (end) user is someone who executes processes on the Unit Operation. The user accesses Open Pectus through a web browser such as Microsoft Edge.

Web Frontend
^^^^^^^^^^^^
The web interface gives an overview of all of the available engines and their status. The user can enter into a specific engine, running or not, create and edit methods, issue machine instructions directly, start and stop execution of a method etc. A live plot shows data from the current method execution in context and a panel of tags shows current process values.

The end user may be identified through a SSO such as Azure so that user preferences wrt. plot setup and tag panels can be retained.

Data is transferred between the Web Frontend and the sever through a WebSockets API.

Aggregator
^^^^^^^^^^
The aggregator aggregates multiple Engines into one interface so that the End User has a single point of entry.

Engine
^^^^^^
The Engine executes commands, runs methods and handles I/O with the Unit Operation it serves. The engine is configured in a Unit Operation Definition which contains information on I/O, process variables (tags) and Machine Instructions.

Engines are decentral and register with the central aggregator.


Check out the :doc:`usage` section for further information, including
how to :ref:`installation` the project.

.. note::

   This project is under active development.

Contents
--------

.. toctree::

   Home <self>
   usage
   api
