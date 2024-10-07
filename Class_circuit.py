import numpy as np

class Circuit:
	def __init__(self):
		self.nodes = set()
		self.components = {}
		self.probes = []
		self.voltage_source = None
		self.ground_node = None

	def add_component(self, name, start, end, value):
		"""adds a component (resistors) to the circuit. 
		the components is a dictionary where the key is the resistor name and the values
		are another dictionary which contains all the nets and values refers the that resistor """
		self.components[name.lower()] = {'start': start, 'end': end, 'value': float(value)}
		self.nodes.add(start) # adds to the nodes set the nets
		self.nodes.add(end)

	def add_probe(self, name, *targets):
		self.probes.append((name, [t.lower() for t in targets]))

	def add_voltage_source(self, node, voltage):
		"""adds a voltage source to the circuit. 
		the votlage source is a dictionary which contains the the node of the source and its value"""
		self.voltage_source = {'node': node, 'voltage': float(voltage)}
		self.nodes.add(node)

	def set_ground(self, node): 
		"""adds a ground node to the circuit object (assuming there is only one ground)"""
		self.ground_node = node
		self.nodes.add(node)

	def solve(self):
		nodes = sorted(list(self.nodes)) # sorts the nodes (nets) list alphabetically
		n = len(nodes)
		node_indices = {node: i for i, node in enumerate(nodes)} 
		# numbering the nodes and put them in a dictionary

		G = np.zeros((n, n)) # creating a zero matrix of conductivity
		I = np.zeros(n) # creating a zero vector of the currents

		for comp in self.components.values(): # running on the nets and values of all resistors
			i, j = node_indices[comp['start']], node_indices[comp['end']]
			# i,j are the appropriate numbering of the nets from the node_indices
			g = 1 / comp['value'] # calculates the conductivity (G = 1/R)
			"""building the conductance matrix.
			   the indexes in the element refers to the nets connectivity of the resistor."""
			G[i, i] += g
			G[j, j] += g
			G[i, j] -= g
			G[j, i] -= g

		vs_node = node_indices[self.voltage_source['node']] # gets the numbering of the voltage source node
		gnd_node = node_indices[self.ground_node] # gets the numbering of the ground node

		""" Clear the row corresponding to the voltage source node in the conductance matrix.
			This is done to prevent the node from being treated as a normal node where KCL would apply.
			We remove the influence of other nodes on this node in the voltage calculation."""
		G[vs_node, :] = 0.0 
		
		""" Set the diagonal element to 1, enforcing a fixed voltage at the voltage source node.
			It ensures that the voltage at the source node will be equal to the voltage provided by the source.
			We know the voltage at this node and do not want it to be computed."""
		G[vs_node, vs_node] = 1.0
		
		""" Set the current vector I at the voltage source node to the source's voltage.
			Its sets the voltage at the source node in the overall system of equations,
			making sure the solver uses this known voltage during the solution process."""
		I[vs_node] = self.voltage_source['voltage']

		# The same thing as before for the ground node
		G[gnd_node, :] = 0.0
		G[gnd_node, gnd_node] = 1.0
		I[gnd_node] = 0.0

		V = self.solve_linear_system(G, I)

		Vt = self.voltage_source['voltage'] # the source voltage is the total one
		# Initialize a variable to hold the total current through the voltage source
		total_current = 0

		# Iterate through all components in the circuit
		for component in self.components.values():
			# Check if the component is connected to the voltage source
			if (component['start'] == self.voltage_source['node'] or 
				component['end'] == self.voltage_source['node']):
        
				# Get the voltage drop across that component
				voltage_drop = np.abs(V[node_indices[component['start']]] - V[node_indices[component['end']]])
        
				# Calculate the current through the component
				current_through_component = voltage_drop / component['value']
        
				# Add the current to the total current
				total_current += current_through_component

		# total_current now holds the sum of currents through all components connected to the voltage source
		It = total_current

		Rt = Vt / It # Calculates the total resistance

		results = {'Rt': Rt, 'Vt': Vt, 'It': It}

		# Iterate through all probes
		for name, targets in self.probes:
			if len(targets) == 1:
				# Probe is for a specific component
				comp_name = targets[0]

				# Retrieve the component directly or find a matching name
				comp = None
				for component_name, component_details in self.components.items():
					if component_name == comp_name or component_name.endswith(comp_name):
						comp = component_details
						break
	
				if comp:
					# Compute voltage and current if the component is found
					voltage_drop = np.abs(V[node_indices[comp['start']]] - V[node_indices[comp['end']]])
					current = voltage_drop / comp['value']
					results[name] = {'V': voltage_drop, 'I': current}
				else:
					# Handle the case where the component is not found
					results[name] = {'V': None, 'I': None}

			elif len(targets) == 2:
				# Probe is for voltage difference between two nodes
				voltage_drop = np.abs(V[node_indices[targets[0]]] - V[node_indices[targets[1]]])
				results[name] = {'V': voltage_drop}

		# Return the results dictionary
		return results

	def solve_linear_system(self, G, I):
		"""solving the system G*V=I"""
		G = np.array(G, dtype=float)
		I = np.array(I, dtype=float)
		V = np.linalg.solve(G, I)
		return V