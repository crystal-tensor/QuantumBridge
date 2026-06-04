# Qiskit Aer Optional Adapter Plan

Status: P1 plan only  
Date: 2026-06-04  

## 1. Why Aer should be optional

Aer is a large simulator ecosystem with its own release cadence and dependencies. QuantumBridge should not vendor or force-install Aer for core usage.

## 2. Native simulator boundary

QuantumBridge native simulation covers small statevector, sampler, estimator, and basic P1 noise metadata. Aer would be used only for advanced simulation backends.

## 3. Minimal Aer adapter capability

Future P2 candidate:

- Detect Aer availability.
- Convert QuantumBridge IR subset to Qiskit circuit.
- Run a selected Aer simulator backend.
- Convert counts/results back to QuantumBridge Result.

## 4. Non-goals

- No Aer source port.
- No full Aer noise model recreation.
- No claim of Aer equivalence.
- No mandatory Aer dependency.

## 5. License compliance

Aer must be reviewed as a separate optional dependency. Attribution and notices must be updated before implementation.

## 6. Test strategy

- Skip if Aer unavailable.
- Run minimal Bell sampler test if installed.
- Verify result adapter metadata states upstream dependency use.

## 7. P2 decision standard

Implement only if users need advanced simulator coverage beyond QuantumBridge native P1 and legal/dependency review passes.

