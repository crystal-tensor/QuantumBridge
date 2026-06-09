# Qiskit Finance Compatibility Strategy

Status: Stage 9A executable portfolio subset update
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

Level 0/1 inventory and passthrough scaffold, Level 2 FinanceResult wrapper, and Stage 9A Level 3 educational portfolio native subset for deterministic mean-variance examples.

## Native Status

Native support is limited to small deterministic binary mean-variance portfolio optimization by exact enumeration. This is educational only and not production finance.

## Unsupported Status

Production portfolio optimization, pricing, credit risk, trading, investment advice, and market-data workflows are unsupported.

## Tests

Tests cover PortfolioOptimization, EuropeanCallPricing, RandomDataProvider availability when installed, dependency-missing errors, wrappers, provenance, unsupported warnings, the deterministic native portfolio example, exact enumeration ordering, serialization, and the optional upstream exact path contract.

## Legal / Attribution

Qiskit Finance remains upstream. No source is vendored.

## Risk

High due to domain-sensitive finance semantics and data-provider terms.
