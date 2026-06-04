# Qiskit Aer P2 Decision

Status: Decision draft  
Date: 2026-06-04  

## Decision

Do not implement Qiskit Aer adapter in the current P1 follow-up. Keep it as a P2 candidate.

## Rationale

- P1 goal is controlled hardening, not advanced simulation parity.
- Aer is a large optional dependency with distinct simulator/noise semantics.
- QuantumBridge P1 noise is basic and metadata-oriented.
- Implementing Aer now would blur P1/P2 boundaries.

## P2 entry criteria for Aer adapter

- GitHub Actions matrix is running.
- Qiskit extra tests pass in CI.
- Legal/dependency review for Aer is complete.
- Minimal adapter design is reviewed.
- Result conversion contract is stable.

## Proposed P2 minimum

- Availability check.
- QuantumBridge IR -> Qiskit circuit subset.
- Run Aer sampler-like backend if installed.
- Convert counts/result metadata to QuantumBridge Result.
- Skip tests if Aer unavailable.

## Non-goals

- No Aer source port.
- No full Aer noise replication.
- No claim of Aer parity.

