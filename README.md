# Electric-Circuit-Analyzer

## Overview of the Electric Circuit Analyzer
The electric circuit analyzer will be implemented using guiding principles. Since the data file contains the connections of each component in the circuit, we can consider them as nodes. Therefore, we will use the Node Voltage Method (KCL) for circuit analysis.

## Circuit Object Implementation in Python
As part of the project preparation, we implemented the Circuit object in Python, which represents the electric circuit. This object allows for the addition of components, definition of voltage sources, and grounding nodes, as well as finding the required values by solving systems of linear equations. The implementation leverages Python's libraries, such as NumPy for efficient matrix operations and data manipulation, as required by the task definition and the data file containing the circuit information.
