# kafka
Kerbal Autonomous Flying Kontrol Autopilot

This is an autopilot based using the python client api from http://krpc.github.io/krpc/python/client.html

It will currently launch most rockets in to a circularised orbit.

## Building

It runs on Python 3

You will need to install [table-loggger](https://pypi.org/project/table-logger/) 
and [numpy](https://pypi.org/project/numpy/)

```
   pip3 install table-logger
```  

```
   pip3 install table-logger
```

## Running

Install the KRPC mod in to Kerbal Space Program and start the server

Put the rocket on the launchpad

Run the [launch script](kafka/launch_to_circular_orbit.py)