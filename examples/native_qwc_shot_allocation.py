# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free actual joint Pauli samples and a conserved measurement budget."""

from quantumbridge import StatevectorDevice
from quantumbridge.qml.tape import Tape
from quantumbridge.transforms import split_non_commuting, execute_transform
from quantumbridge.utils.math import Hamiltonian, PauliX, PauliZ


def main():
    terms = [(2.,PauliX(0)),(3.,PauliX(0).tensor(PauliZ(1))),(.4,PauliZ(0))]
    tape = Tape(2,shots=[1001,(2001,2)],seed=2026)
    tape.ry(.7,0)
    tape.expval(Hamiltonian(terms))
    reference = StatevectorDevice().expectation(tape.circuit,Hamiltonian(terms))
    value,metadata = execute_transform(tape,split_non_commuting(shot_dist="weighted"),return_metadata=True)
    details = metadata["stages"][0]["postprocessing_metadata"][0]
    print("original_terms:",[(c,p.terms) for c,p in terms])
    print("generated_groups:",details["groups"])
    for execution in metadata["executions"]:
        for partition in execution["partitions"]:
            receipt = partition["joint_measurements"][0]
            print({key:receipt[key] for key in ("execution_id","basis","shots","sample_count","seed",
                                               "source_expectation_contributions","source_group_standard_errors","provenance")})
    for index,(energy,partition) in enumerate(zip(value,details["partitions"])):
        standard_error = partition["source_measurements"][0]["standard_error"]
        assert partition["total_physical_shots"] == [1001,2001,2001][index]
        assert abs(energy-reference) < 8*standard_error + .01
        print({"partition":index,"energy":energy,"analytic_reference":reference,
               "standard_error":standard_error,"total_physical_shots":partition["total_physical_shots"]})
    print("Joint covariance is included; B5 transformed gradients are not claimed.")


if __name__ == "__main__":
    main()
