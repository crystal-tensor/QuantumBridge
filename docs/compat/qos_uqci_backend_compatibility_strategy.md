# QOS-UQCI Backend Compatibility Strategy

Stage 10A promotes QOS-UQCI compatibility from planning to a bounded executable
offline slice.

QuantumBridge supports:

- QuantumBridge IR -> QOS-UQCI clean-room IR;
- QOS-UQCI offline job spec;
- DeviceSpec / CalSet / Manifest metadata;
- OpenQASM compatibility artifact;
- offline mock runtime returning QuantumBridge backend result schema;
- optional upstream package boundary metadata when installed separately.

This is not production QOS runtime support. It does not access cloud services,
read tokens, execute real hardware, copy QOS-UQCI source, or imply official
endorsement.
