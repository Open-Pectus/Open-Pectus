# Websockets example

This is a small Websockets example which serves as a proof-of-concept wrt. the Open Pectus architecture.

## Three pieces to the puzzle
### Aggregator
The Aggregator allows engines to register themselves and accept the data they push. Users can also connect and subscribe to data from engines and send commands back to the engines.

### Engine
The engine connects with the Aggregator and registers itself. After registration it will periodically send data to the aggregator.

### User
Users can connect to the Aggregator and subscribe to data from a specific engine.

## Use
To get started `pip install fast_api_pubsub`.

You need three sessions started sequentially:
1. `python aggregator.py`
2. `python engine.py`
3. `python user.py`

It is OK to launch multiple engines and multiple users.

Expect the following:
* The Aggregator will print log statements
* The Engine will print it's (randomly generated) engine ID and a randomized integer:
```
$ python engine.py
>> 0257 0545
>> 0257 0704
>> 0257 0243
>> 0257 0288
>> 0257 0106
>> 0257 0959 # user.py was running from this point onwards.
Engine was served an action: {'a': 5, 'b': 4}
>> 0257 0522
Engine was served an action: {'a': 5, 'b': 4}
```
* The User will print the engine ID from which it is receiving data as well as the randomized integer. It will call the `action` method on the engine that it receives data from.
```
$ python user.py
<< 0257 0522
<< 0257 0710
<< 0257 0332
<< 0257 0866
<< 0257 0208
<< 0257 0783
```