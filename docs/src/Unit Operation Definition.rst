.. role:: console(code)
   :language: console
.. role:: python(code)
   :language: python
.. role:: pcode(code)
   :language: pcode

.. _unit_operation_definition:

Unit Operation Definition
=========================
This chapter contains information about creating and configuring a Unit Operation Definition (UOD). Its intended audience is primarily engineers.

A UOD is a python code file that is loaded by the OpenPectus Engine. It describes the capabilities of a physical process unit and enables the engine to communicate with the hardware.

.. contents:: Table of Contents
  :local:
  :depth: 3

UOD File
--------
.. _found here: https://github.com/Open-Pectus/Open-Pectus/blob/main/openpectus/engine/configuration/demo_uod.py

A UOD file is a Python file ending with :console:`.py`. A concise demo UOD file is shipped with Open Pectus and can be `found here`_. It is a good starting point for development of a new UOD.

The minimal content of a UOD file is:

.. code-block:: python

   def create() -> UnitOperationDefinitionBase:
       builder = UodBuilder()

       return (
           builder
           .with_instrument("Unit Operation Name")
           .with_author("Author Name", "author@email.org")
           .with_filename(__file__)
           .with_location("Site / Building / Room")
           .with_hardware_opcua(host="opc.tcp://192.168.0.1:4840")

           <additional details>

           .build()
       )

The :console:`<additional details>` are elaborated in the following.


Required options
^^^^^^^^^^^^^^^^

The following options are mandatory:

- instrument name: The name of the instrument/unit. Usually the same name as the UOD file but all characters are permitted, including spaces and dashes.
- author: The name and email address of the author of the UOD.
- filename: The file name of the UOD. Set with `with_filename(__file__)` to automatically fill in the correct file name.
- location: The name of the location that houses the hardware unit.
- hardware: See :ref:`hardware_section`

.. todo::

    Provide rationale/explanation of usage of the above options to the UOD author.

.. _hardware_section:

Hardware
^^^^^^^^
.. _LabJack hardware: https://labjack.com


Open Pectus has builtin support for the OPC-UA protocol as well as `LabJack hardware`_. The UOD must specify which hardware to use by using one of the builder methods: :python:`with_hardware_opcua(host)` or :python:`with_hardware_labjack(serial_number)`.

It is also possible to use a combination of sources with the :python:`Composite_Hardware` class.

Registers
^^^^^^^^^
Registers are 'slots' in the hardware that can be read and/or written. The available registers depend entirely on the hardware.

Registers are defined using the `with_hardware_register(self, name: str, direction, **options):`
builder method. For OPC-UA, this may look like:

.. code-block:: python

   with_hardware_register("FT01", "Read", path='Objects;2:System;3:FT01')

Note that the :console:`name` argument specifies the name to use for the register inside Open Pectus while the :console:`path` option specifies how to refer to the register when communicating with the hardware.

Registers are not used directly. Instead register values are wrapped in instances of the :python:`Tag` class. Two special register options :python:`to_tag` and :python:`from_tag` specify how to convert between the register values (the raw values read from the hardware)  and :python:`tag` values (the values used in P-code). If these options are not set, no conversion of the value is performed.

As an example, a unit may have a valve that is exposed as a register whose values are the integers 0 and 1. The :python:`to_tag` and :python:`from_tag` options can be used to map theses values to a tag with the string values 'On' and 'Off' which would be a more natural choice for process operators.

Tags
^^^^
A `tag` is a container for a value, typically a value that comes from a register. Other examples are the built in system tags and any custom tags that the UOD may define.

Tag values can be accessed from P-code, for example to express conditions based on the values while the P-code method runs.

Besides holding a value, a tag also has these properties:

* :python:`name`: The name of the tag. Typically the same as the name of the register that provides the tag's value
* :python:`unit`: The unit of the value or None for values with no unit. Example units are `kg`, `min`, `L`, and `L/h`
* :python:`tick_time`: The time of the last value update, measured in seconds since the Epoch
* :python:`direction`: Specifies how the value of the tag is obtained
  * :python:`INPUT` - Tag is read from hardware, e.g. a sensor
  * :python:`OUTPUT` - Tag is written to hardware, e.g. an actuator
  * :python:`NA` - Tag is calculated/derived and neither read from or written to hardware
  * :python:`UNSPECIFIED` - Not specified. The system may not be able to handle its values properly
* :python:`safe_value`: Specifies a value that represents a safe position, e.g. an `OFF` value for a valve.

To define a tag, use the :python:`with_tag` builder method. If a tag is given the same name as a register, the two are automatically matched. This means that (depending on the directions of the register and tag), the register's value and the tag are synchronized as appropriate.

.. note::
   This API is not yet stable. The :python:`with_tag` method is expected to have variations for most known use cases, e.g. :python:`with_tag_choice` and :python:`with_tag_reading` instead of the current implementation where the concrete :python:`Tag` instance is given. We need to know more concrete tags to define this API.


Built in system tags
````````````````````

Open Pectus contains a number of tags that are always available and which are not related to specific hardware. See :ref:`built_in_system_tags` for details.

Commands
^^^^^^^^

The UOD can define custom commands. These are python functions that define behavior for the unit and have access to the hardware. As an example, we might want a :pcode:`Reset` command that performs a number of things, and make a simple :pcode:`Reset` command available in P-code.

We could additionally expose the :pcode:`Reset` command as a button in the web frontend using :ref:`process_values`.

The actual implementation of a command should be a function in the UOD, for example

.. code-block:: python

   def reset(cmd: UodCommand, **kvargs) -> None:
       # implement command logic
       # possibly use one or more tags, available as cmd.context.tags
       # posibly using hardware directly, available as cmd.context.hwl
       # possily using the command instance, available as cmd.
       # raise ValueError if an error occurs, to report it to the user.
       pass

To make the function available as an Open Pectus command, it must be registered using :python:`with_command(name="Reset", exec_fn=reset)`.

Additional arguments are available to :python:`with_command` that allows initialization, finalization and custom argument parsing. 

Command arguments
`````````````````

Say we want to define a command with the pcode:

.. code-block:: pcode

   Power: 0.5


, i.e. a command that takes a single argument of type :python:`float`.

The python function of the command may look like this:

.. code-block:: python

   def power(cmd: UodCommand, number):
       number = float(number)
       ...

This can be achieved using the :python:`with_command_regex_arguments` method:

.. code-block:: python

   .with_command_regex_arguments(
       name="Power",
       exec_fn=power,
       arg_parse_regex=RegexNumber(units=None)
       )

This allows Open Pectus to parse the argument to a :python:`float` via a predefined regular expression, and pass it to the :python:`power` function when the command is executed.

Note that, currently, the regex will not convert the argument to a float. The execution function needs to do that conversion: :python:`number = float(number)`. The regex does ensure that this conversion will work. If the value cannot be parsed as a float, the regex parsing function will pause the method and alert the user.

Note that the argument names to the exec function are defined in the regular expression. :python:`RegexNumber` defines 'number' (and 'number_unit' if one or more units are given). The exec function argument must use the same name. Validation is built in to help ensure that arguments and names match up correctly. This validation runs at engine startup.

There are predefined regex parsers for numbers (:python:`RegexNumber`), text (:python:`RegexText`) and categorical values (:python:`RegexCategorical`).


General Arguments and Parsers
`````````````````````````````

It is advised to use :python:`with_command_regex_arguments` and one of the predefined regular expressions for parsing if possible. 

However, in the general case, to support multiple arguments of different types, a custom parser can be defined. This can be achieved using a custom command parser passed to `with_command`.

.. note::
   Custom parsing cannot be validated during engine startup so any argument or name mismatch between argument parser and execution function is not caught until the command is executed. In other words - make sure to test it properly.


.. _process_values:

Process values
^^^^^^^^^^^^^^
In order for a `tag` to be shown in the Open Pectus web frontend, it must be defined as a process value with :python:`with_process_value`. This has three purposes:

#. Select the tag to be displayed
#. Display the tag's current value (and unit if available)
#. Possibly allow the use to interact with the value, e.g. by setting a new value or executing a command that is related
   to the tag.

The following types of interaction is supported:

* :python:`with_process_value` - Read-only. The tag value is displayed but it cannot be modified.
* :python:`with_process_value_entry` - Read/write. The tag value is displayed and its value can be changed by clicking the value and typing the new desired value.
* :python:`with_process_value_choice`. The tag value is displayed and when clicked, a list of commands  are shown. When a command from the list is selected, the corresponding command is executed.


Common scenarios
^^^^^^^^^^^^^^^^

The Demo Uod included with Open Pectus includes most of the supported scenarios. It is located in :console:`openpectus/engine/configuration/demo_uod.py`.

.. todo::
   * Show a few examples with register, tag, command and process value
   * Cover choice commands
   * Show example using regular expression helpers


.. _built_in_system_tags:

Built In System Tags
^^^^^^^^^^^^^^^^^^^^

A number of system tags are built into Open Pectus and are automatically set by the system.

System Tags Reference
`````````````````````

* Connection Status: :console:`Connected`, :console:`Disconnected`

  State of hardware connection. Is affected by error recovery so it will not show `Disconnected` until 
  recovery has been attempted and failed multiple times.

* Method Status: :console:`OK`, :console:`Error`

  Error state of the current method.

* System State:
  :console:`Running`, :console:`Paused`, :console:`Holding`, :console:`Waiting`, :console:`Stopped`, :console:`Restarting`

  State of the current run / method.
  If :console:`Paused` and :console:`Holding` simultaneously, then :console:`Paused` takes priority.

* Clock:

  Number of seconds since epoch.

* Run Time:

  Is reset to 00:00:00 when user starts method. Run timer increments when `System State` is not :console:`Stopped`.

* Process Time:

  Is reset to :console:`00:00:00` when user starts method. Process time increments when `System State` is :console:`Run`.

* Block Time:

  Block Time maintains the process time of each block. It starts at zero and increments when `System State` is :console:`Run`.
  When entering a new block it is reset to zero and when leaving a block, its value is restored to the time of the outer block plus the time of the inner block.
  
  `Block Time` is reset to :console:`00:00:00` when leaving a block due to :pcode:`End block` or :pcode:`End blocks` commands. Block time increments when `System State` is :console:`Run`.

* Accumulated Volume:

  Set to :console:`0.00 L` when user starts method.

* Block Volume:

  Set to :console:`0.00 L` when leaving a block due to :pcode:`End block` or :pcode:`End blocks` commands.

* Accumulated CV:

  Set to :console:`0.00 CV` when user starts method.

* Block CV:

  Set to :console:`0.00 CV` when leaving a block due to :pcode:`End block` or :pcode:`End blocks` commands.

* Mark:

   Holds value(s) assigned by the :pcode:`Mark` command. Value is reset to the empty string each time archiver saves the current tag values.
  
* Base: :console:`L`, :console:`h`, :console:`min`, :console:`s`, :console:`mL`, :console:`CV`,  :console:`g`, :console:`kg` etc.

* Run Counter:
  Integer value which can be assigned by the :pcode:`Run counter` command or incremented by console:`1` by the
  :pcode:`Increment run counter` command. The initial value is :console:`0` on engine startup.

* `Batch`:
  Hold value assigned by :pcode:`Batch` command.
