
from openpectus.aggregator.routers.dto import CommandExample

examples_demo = [
    CommandExample(name="Some Example", example="Some example text"),
    CommandExample(name="Watch Example", example="""
Watch: Block Time > 3s
    Mark: A
Mark: X

Watch: Block Time > 7s
    Mark: B
Mark: Y""")
]

examples = [
    CommandExample(name="Alarm", example="""
# Alarm is a block that executes when a condition is satisfied repeatedly.

# Example 1
Alarm: Block Time > 5 s
    End block

Block: A
    Mark: A

Block: B
    Mark: B

Block: C
    Mark: C

Stop

# Example 2
Base: s
Batch: Hello

Alarm: Batch = Hello
    3.0 Batch: User

Alarm: Batch = User
    3.0 Batch: Hello
"""),
    CommandExample(name="Base", example="""
# Example 1:
Base: CV # Measure time in column volumes

# Example 2:
Base: min # Measure time in minutes

# Example 3:
Base: s # Measure time in seconds
"""),
#     CommandExample(name="Batch", example="""
# """),
    CommandExample(name="Block", example="""
# Example 1:
Block: Elution
    Mark: Start elution
    End block
    # Open proper valves etc
"""),
    CommandExample(name="End block", example="""
# End the block currently executing.

# Example 1
Block: This is a block
    1.0 End block
# Block is no more.

# Example 2
Block: Layer 1
    Block: Layer 2
        End block
    # We have escaped the block "Layer 2"
    # but are still in "Layer 1".
"""),
    CommandExample(name="End blocks", example="""
# End all currently executing blocks.

# Example 1
Block: This is a block
    1.0 End block
# Block is no more.

# Example 2
Block: Layer 1
    Block: Layer 2
        End blocks
# We have escaped both blocks.
"""),
    CommandExample(name="Error", example="""
# Make a statement to the log file.

Error: Hello.
"""),
    CommandExample(name="Hold", example="""
# Hold current output values but do not
# progress with respect to time.

# Example 1
# Open outlet VA38 for one minute, then VA37.
Outlet: VA38
Hold: 1 min
Outlet: VA37
"""),
    CommandExample(name="Increment run counter", example="""
# Add 1 to the Run Counter.

# Example 1
Watch: Run Counter > 3
    Stop

Wait: 10 s

Increment run counter

Restart
"""),
    CommandExample(name="Info", example="""
# Make a statement to the log file.

Info: Hello.
"""),
    CommandExample(name="Mark", example="""
# Make a note in the data file at the current point in time.

# Example 1
Wait: 5 s
Mark: 5 seconds have passed.
"""),
    CommandExample(name="Pause", example="""
# Pause execution of commands
# and time. Put outputs into safe state.

# Example 1
Outlet: VA38
Pause: 1 min # Outlet is closed for 1 minute.
"""),
    CommandExample(name="Restart", example="""
# Stop execution, then start the method again.

# Example 1
Restart
"""),
    CommandExample(name="Run counter", example="""
# Assign a value to the Run Counter.

# Example 1
Run counter: 3
"""),
#     CommandExample(name="Simulate", example="""
# # Simulate a value of a measured tag.

# # Example 1
# Simulate: UV01 Absorbance = 1 AU
# """),
#     CommandExample(name="Simulate off", example="""
# # Stop simulation of measured tag.

# # Example 1
# Simulate: UV01 Absorbance = 1 AU
# Wait: 5s
# Simulate off: UV01 Absorbance
# """),
    CommandExample(name="Stop", example="""
# Stop execution.

# Example 1
Stop
"""),
    CommandExample(name="Wait", example="""
# Holds execution of commands for the specified duration.

# Example 1
# Open outlet VA38 for one minute, then VA37.
Outlet: VA38
Wait: 1 min
Outlet: VA37
"""),
    CommandExample(name="Warning", example="""
# Make a statement to the log file.

Warning: Hello.
"""),
    CommandExample(name="Watch", example="""
# Watch is a block that executes when a condition is satisfied.

# Example 1:
Watch: Block Time > 1 min
    Mark: One minute has passed

# Example 2:
Watch: Run Counter > 3
    Stop # Stop after 3 runs have been executed.
Wait: 5 s
Restart
"""),
]
