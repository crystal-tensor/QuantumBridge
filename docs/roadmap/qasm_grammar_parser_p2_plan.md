# QASM Grammar Parser P2 Plan

Status: P2 planning draft  
Date: 2026-06-04  

## Current P1 state

QuantumBridge currently uses a regex-based OpenQASM 2.0 subset parser. It supports common P1 constructs but is not a complete grammar parser.

## Why a grammar parser is needed

- Better syntax errors.
- Easier extension to expressions.
- Safer parsing of declarations and statements.
- Cleaner separation between parsing and IR construction.
- Better compatibility testing.

## Candidate approach

P2 should introduce a small parser pipeline:

1. Lexer for comments, identifiers, numbers, punctuation, and strings.
2. Parser for OpenQASM 2.0 subset statements.
3. AST nodes for declarations, gates, measurements, barriers, and includes.
4. AST-to-QuantumBridge IR lowering.
5. Structured diagnostics with source line/column where practical.

## P2 supported subset target

- OPENQASM 2.0 header.
- qelib1 include.
- qreg / creg.
- Standard P1 gates plus selected P2 gates.
- Measurements.
- Barrier.
- Numeric expressions for angles.

## Out of scope for first grammar parser

- Full QASM3.
- Dynamic circuits.
- User-defined gates.
- Classical conditions.
- Full expression language.

## Testing strategy

- Golden parser tests for valid subset.
- Negative tests with line/column diagnostics.
- Roundtrip tests through QuantumBridge IR.
- Compatibility tests against selected public OpenQASM examples that are license-reviewed.

## Acceptance standard

P2 parser replaces regex parser for supported subset and preserves all P1 QASM tests.

