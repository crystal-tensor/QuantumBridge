# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
from pathlib import Path
from .limits import SerializationLimits
from .errors import FormatValidationError, ResourceLimitError


class BoundedParts(list):
    def __init__(self,limits,format):
        super().__init__()
        self.limits,self.format,self.size = limits,format,0
    def append(self,value):
        self.size += len(value)
        self.limits.check("max_input_bytes",self.size,format=self.format)
        super().append(value)
    def extend(self,values):
        for value in values: self.append(value)


def read_input(source, *, binary=False, limits=None, format=None):
    limits = limits or SerializationLimits()
    if hasattr(source,"read"):
        data = source.read(limits.max_input_bytes+1)
    else:
        with Path(source).open("rb" if binary else "r", **({} if binary else {"encoding":"utf-8"})) as stream:
            data = stream.read(limits.max_input_bytes+1)
    expected = bytes if binary else str
    if not isinstance(data,expected): raise FormatValidationError("Incorrect stream mode.",format=format)
    limits.check("max_input_bytes",len(data) if binary else len(data.encode("utf-8")),format=format)
    return data


def write_output(destination, data):
    if hasattr(destination,"write"): destination.write(data)
    else:
        with Path(destination).open("wb" if isinstance(data,bytes) else "w",**({} if isinstance(data,bytes) else {"encoding":"utf-8"})) as stream:
            stream.write(data)


def register_specs(circuit):
    specs = circuit.metadata.get("registers")
    if specs is None:
        specs = [{"kind":"q","name":"q","bits":list(range(circuit.num_qubits))}]
        if circuit.num_bits: specs.append({"kind":"c","name":"c","bits":list(range(circuit.num_bits))})
    used, names = {"q":set(),"c":set()}, set()
    for spec in specs:
        kind, name, bits = spec["kind"], spec["name"], spec["bits"]
        if kind not in used or not isinstance(name,str) or not name or name in names or not bits:
            raise FormatValidationError("Invalid/duplicate register declaration.")
        width = circuit.num_qubits if kind == "q" else circuit.num_bits
        if any(isinstance(bit,bool) or not isinstance(bit,int) or not 0 <= bit < width or bit in used[kind] for bit in bits) or len(set(bits)) != len(bits):
            raise FormatValidationError("Invalid/aliased register mapping.")
        used[kind].update(bits); names.add(name)
    if used != {"q":set(range(circuit.num_qubits)),"c":set(range(circuit.num_bits))}:
        raise FormatValidationError("Registers must cover each wire once; alias/loose-bit export is unsupported.")
    return specs
