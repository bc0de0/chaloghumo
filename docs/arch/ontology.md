# System Ontology: ChaloGhumo Data Structures & Primitives

This document defines the core entities and data primitives that form the backbone of the ChaloGhumo recommendation engine.

## 1. Core Primitives

### A. TemporalUnit

Represents time in a contextual sense rather than just a timestamp.

- `Season`: [Spring, Summer, Autumn, Winter]
- `PeakStatus`: [OffPeak, Shoulder, Peak]
- `LocalTime`: ISO-8601 with timezone context.

### B. GeographicPoint

- `Coordinates`: {lat: float, lng: float}
- `Elevation`: meters (critical for temperature/weather modeling)
- `RegionType`: [Coastal, Alpine, Urban, Rural, Desert]

### C. Signal

A real-time data point with a confidence score.

- `Type`: [Weather, Crowds, Temperature, Pricing]
- `Value`: float | string
- `Confidence`: 0.0 - 1.0 (epistemic certainty)
- `Source`: String (identifier of the data provider)

## 2. Domain Objects

### A. The Personal Context (`UserPersona`)

Represents the subjective state and requirements of the traveler.

- `Preferences`: Map of weights (e.g., `adventure: 0.8`, `relaxation: 0.2`)
- `Constraints`: List of `Constraint` objects (e.g., `max_budget`, `mobility_requirements`)
- `Mood`: Semantic string (e.g., "seeking solitude", "vibrant energy")

### B. The Environmental State (`EnvironmentState`)

The objective physical conditions of a destination.

- `Temperature`: {current: float, feels_like: float, trend: [Rising, Falling, Stable]}
- `Conditions`: [Clear, Overcast, Precipitation, Extreme]
- `NaturalEvents`: List of active events (e.g., "Cherry Blossom Peak", "Monsoon Start")

### C. The Societal State (`SocialState`)

Real-world human constraints.

- `CrowdDensity`: 0.0 (Empty) to 1.0 (Maximum Capacity)
- `Availability`: Percentage (0-100) of primary infrastructure (hotels, transport)
- `LocalStatus`: [Normal, Holiday, EventActive, Restricted]

## 3. Entity Definitions

### A. Destination

The primary unit of recommendation.

- `ID`: UUID
- `Name`: String
- `Geo`: `GeographicPoint`
- `BaseVibe`: Semantic tags (e.g., "Bohemian", "High-Tech", "Rustic")
- `DynamicState`: `EnvironmentState` + `SocialState` (updated via Signal ingestion)

### B. Recommendation

The final synthesized output.

- `DestinationID`: Reference to `Destination`
- `MatchScore`: 0.0 - 1.0
- `ReasoningChain`: List of logic steps explaining the match.
- `ContextSnapshot`: The exact state of the three domains at the time of generation.

## 4. Constraint Model

- **HardConstraint**: Boolean logic. If `false`, the destination is pruned immediately.
- **SoftConstraint**: Weight-based logic. Influences the `MatchScore` but does not prune.
