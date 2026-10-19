# Offline DeviceSpec and directed physical routing; no token or cloud request.
from quantumbridge import Circuit, StatevectorDevice
from quantumbridge.compiler import Target, native_transpile
from quantumbridge.compat.qos_uqci.devicespec_adapter import build_devicespec, validate_devicespec


def main():
    spec = build_devicespec(num_qubits=3)
    validate_devicespec(spec)
    circuit = Circuit(3).x(0).cx(0,2)
    compiled = native_transpile(circuit,target=Target.from_device_spec(spec))
    print("Routing:",compiled.metadata["routing"])
    print("Probability of 101:",StatevectorDevice().probabilities(compiled)["101"])
    print("Offline only: hardware_access=False, token_read=False")


if __name__ == "__main__": main()
