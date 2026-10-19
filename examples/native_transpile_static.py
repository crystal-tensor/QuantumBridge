# Independent native compiler and static timing example; no hardware access.
from quantumbridge import Circuit, StatevectorDevice
from quantumbridge.compiler import Target, native_transpile


def main():
    circuit = Circuit(2).h(0).cx(0,1).ry(.3,1)
    target = Target(2,("rz","sx","x","cx"),[(0,1)],dt=1e-9,
                    durations={"rz":0.,"sx":4e-9,"x":8e-9,"cx":16e-9})
    compiled, report = native_transpile(circuit,target=target,scheduling_method="asap",return_report=True)
    print("Probabilities:",StatevectorDevice().probabilities(compiled))
    print("Schedule:",report["analyses"]["schedule"])


if __name__ == "__main__": main()
