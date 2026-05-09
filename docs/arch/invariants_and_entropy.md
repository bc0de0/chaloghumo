# System Invariants & Entropy Management

This document defines the immutable rules (Invariants) of the ChaloGhumo reasoning engine and our strategy for managing informational decay (Entropy).

## 1. System Invariants

System invariants are the logical constants that must hold true at all times for a recommendation to be considered valid.

### A. The Safety Invariant

No destination shall be ranked above the "Viability Threshold" if an active `Extreme` environmental signal (e.g., Severe Weather Alert, Natural Disaster) is detected within the destination's `GeographicPoint` buffer.

### B. The Contextual Consistency Invariant

A recommendation is invalid if its `ContextSnapshot` contains contradictory signals (e.g., `Conditions: Snowing` while `Temperature: 35°C`). Such states trigger an automatic `SignalRevalidation` event.

### C. The Hard Constraint Invariant

If any `UserPersona.HardConstraint` is evaluated as `false` for a specific `DestinationID`, that destination must be pruned from the candidate set regardless of its `MatchScore`.

## 2. Entropy & Information Decay

In a real-time recommendation system, entropy is the measure of uncertainty introduced by time and noise.

### A. Signal Decay

The epistemic certainty of a `Signal` decreases as its age increases.

- **High-Velocity Signals** (e.g., Weather, Crowd Density): Decay half-life of 15 minutes.
- **Low-Velocity Signals** (e.g., Seasonality, BaseVibe): Decay half-life of 30 days.

### B. The Entropy Buffer

When a signal's `Confidence` falls below `0.4` due to decay, the system must either:

1. Trigger an immediate refresh from the `Source`.
2. Apply a "Fuzzy Weighting" that penalizes the `MatchScore` proportional to the uncertainty.

### C. Signal Noise Filtering

Entropy introduced by conflicting data sources is managed through **Weighted Truth Synthesis**. If two sources provide conflicting values for the same `Signal`, the system favors the source with the higher historical `Confidence` score for that specific `RegionType`.

## 3. State Reconciliation

The system performs a "Consistency Check" every 300 seconds to ensure the current `DynamicState` of all cached destinations aligns with the latest ingested signals, preventing "Ghost Recommendations" (suggesting a destination based on stale, high-value signals).
