"""
Some stops are close to each other, but with different stop sequence.

An example

Stop A, stop sequence 5
Stop B, stop sequence 17

We Know:

In stop A a bus will need to travel more than stop B to arrive to the parent station

STOP DIFFERENCE is a constant used by the algorithm to determine if there is a
significant difference between the stops to display a different route alternative
"""
STOP_DIFFERENCE = 8
