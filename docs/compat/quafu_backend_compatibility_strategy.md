# Quafu Backend Compatibility Strategy

Stage 10A promotes Quafu / pyquafu compatibility from planning to a bounded
executable offline slice.

QuantumBridge supports:

- QuantumBridge IR -> Quafu-compatible clean-room payload;
- Quafu offline job spec;
- offline mock backend returning QuantumBridge backend result schema;
- optional pyquafu package boundary metadata when installed separately.

This is not a full pyquafu replacement or production backend. It does not access
cloud services, read tokens, execute real hardware, vendor Quafu source, or imply
official endorsement.
