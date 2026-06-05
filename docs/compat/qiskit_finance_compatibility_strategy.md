# Qiskit Finance Compatibility Strategy

Status: Stage 7 planning  
Detailed companion: `docs/compat/strategy/qiskit_finance_compatibility_strategy.md`

## Scope

Portfolio applications, option-pricing applications, data providers, uncertainty models, and finance circuits.

## Non-goals

No production finance, pricing accuracy, risk advisory, or data-provider service claim.

## Optional Dependency

Install with `.[qiskit-finance]`.

## Inventory Status

Current local environment records dependency-not-installed placeholders; remote extra CI should validate installed inventory.

## Adapter Status

Level 0/1 scaffold only.

## Native Status

No native finance implementation.

## Unsupported Status

Production portfolio optimization, pricing, credit risk, and market-data workflows are unsupported.

## Tests

Tests cover PortfolioOptimization, EuropeanCallPricing, RandomDataProvider availability when installed, dependency-missing errors, wrappers, provenance, and unsupported warnings.

## Legal / Attribution

Qiskit Finance remains upstream. No source is vendored.

## Risk

High due to domain-sensitive finance semantics and data-provider terms.
