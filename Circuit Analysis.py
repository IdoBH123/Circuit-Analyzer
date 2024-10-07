from Class_circuit import Circuit

def parse_circuit_file(filename):
	# Splitting the components in the file to the proper category
    circuit = Circuit() # Creating new circuit object
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split() # converts the line to a list with all the data
            if not parts:
                continue
            if parts[0].startswith('R'): # adds the resistors components to the circuit object
                circuit.add_component(parts[0], parts[1], parts[2], parts[3])
            elif parts[0] == 'Probe': # adds the probes to the circuit object
                circuit.add_probe(parts[1], *parts[2:])
            elif parts[0].startswith('P'): # adds the power source to the circuit object
                circuit.add_voltage_source(parts[1], parts[2])
            elif parts[0].startswith('G'): # adds the ground node to the circuit object
                circuit.set_ground(parts[1])
    return circuit

def write_results_to_file(file, results):
	# writing the final results in the output file
    out = file+'.out'
    with open(out, 'w') as file:
        file.write(f"Rt={results['Rt']:.2f}\t\tVt={results['Vt']:.1f}\t\tIt={results['It']:.4f}\n")
        for name, data in results.items():
            if name not in ['Rt', 'Vt', 'It']:
                if 'I' in data: # writing the resistors probes in file
                    file.write(f"{name}\tV={data['V']:.4f}\tI={data['I']:.6f}\n")
                else: # writing the voltage drop probes in file
                    file.write(f"{name}\tV={data['V']:.4f}\n")

    print(f"Results have been written to {out}")

def main():
    file = input("Please write the input file name: ") # input filename
    filename = file + ".cir"
    circuit = parse_circuit_file(filename)
    results = circuit.solve()
    write_results_to_file(file, results)

if __name__ == "__main__":
    main()