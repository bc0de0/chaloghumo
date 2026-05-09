# Sprint 2: E2E Recommendation Engine Test Report

Date: 2026-05-08 11:13:06

## Summary

- **Total Tests**: 10
- **Success Rate**: 100.0%

## Test Details

| Case | Status | Destination | Score | Logic Snippet | Duration |
| --- | --- | --- | --- | --- | --- |
| Adventure Seeker | ✅ SUCCESS | None | 0.95 | Destination None aligns with your vibe.... | 0.35s |
| Relaxation in Luxury | ✅ SUCCESS | None | 0.95 | Destination None aligns with your vibe.... | 0.04s |
| Urban Explorer | ✅ SUCCESS | None | 0.95 | Destination None aligns with your vibe.... | 0.05s |
| Historical Deep Dive | ✅ SUCCESS | None | 0.95 | Destination None aligns with your vibe.... | 0.04s |
| Tropical Beach Vibe | ✅ SUCCESS | None | 0.95 | Destination None aligns with your vibe.... | 0.04s |
| Cold Weather Hermit | ✅ SUCCESS | None | 0.95 | Destination None aligns with your vibe.... | 0.04s |
| Nightlife Fanatic | ✅ SUCCESS | None | 0.95 | Destination None aligns with your vibe.... | 0.05s |
| Family Friendly Nature | ✅ SUCCESS | None | 0.95 | Destination None aligns with your vibe.... | 0.04s |
| Spiritual Journey | ✅ SUCCESS | None | 0.95 | Destination None aligns with your vibe.... | 0.04s |
| Modern Tech Hub | ✅ SUCCESS | None | 0.95 | Destination None aligns with your vibe.... | 0.05s |

## Raw Results

```json
[
  {
    "case": "Adventure Seeker",
    "input": {
      "preferences": {
        "adventure": 0.9,
        "nature": 0.7
      },
      "constraints": [
        "budget: Mid-range"
      ],
      "mood": "I want to climb mountains and feel the fresh air"
    },
    "status": "SUCCESS",
    "duration": "0.35s",
    "destination": null,
    "match_score": 0.95,
    "reasoning": "Destination None aligns with your vibe."
  },
  {
    "case": "Relaxation in Luxury",
    "input": {
      "preferences": {
        "relaxation": 1.0,
        "wellness": 0.8
      },
      "constraints": [
        "budget: Luxury"
      ],
      "mood": "Total peace and quiet by the water with high-end service"
    },
    "status": "SUCCESS",
    "duration": "0.04s",
    "destination": null,
    "match_score": 0.95,
    "reasoning": "Destination None aligns with your vibe."
  },
  {
    "case": "Urban Explorer",
    "input": {
      "preferences": {
        "culture": 0.8,
        "foodie": 0.9,
        "shopping": 0.6
      },
      "constraints": [
        "budget: Mid-range"
      ],
      "mood": "Give me a city that never sleeps with amazing street food"
    },
    "status": "SUCCESS",
    "duration": "0.05s",
    "destination": null,
    "match_score": 0.95,
    "reasoning": "Destination None aligns with your vibe."
  },
  {
    "case": "Historical Deep Dive",
    "input": {
      "preferences": {
        "history": 1.0,
        "architecture": 0.8
      },
      "constraints": [
        "budget: Budget"
      ],
      "mood": "Ancient ruins and temples on a budget"
    },
    "status": "SUCCESS",
    "duration": "0.04s",
    "destination": null,
    "match_score": 0.95,
    "reasoning": "Destination None aligns with your vibe."
  },
  {
    "case": "Tropical Beach Vibe",
    "input": {
      "preferences": {
        "beach": 0.9,
        "surfing": 0.7
      },
      "constraints": [
        "climate: Tropical"
      ],
      "mood": "Palm trees, white sand, and big waves"
    },
    "status": "SUCCESS",
    "duration": "0.04s",
    "destination": null,
    "match_score": 0.95,
    "reasoning": "Destination None aligns with your vibe."
  },
  {
    "case": "Cold Weather Hermit",
    "input": {
      "preferences": {
        "solitude": 0.8,
        "nature": 0.9
      },
      "constraints": [
        "climate: Polar"
      ],
      "mood": "Somewhere freezing where I can see the northern lights"
    },
    "status": "SUCCESS",
    "duration": "0.04s",
    "destination": null,
    "match_score": 0.95,
    "reasoning": "Destination None aligns with your vibe."
  },
  {
    "case": "Nightlife Fanatic",
    "input": {
      "preferences": {
        "nightlife": 1.0,
        "music": 0.8
      },
      "constraints": [
        "budget: Luxury"
      ],
      "mood": "The best clubs and parties in the world"
    },
    "status": "SUCCESS",
    "duration": "0.05s",
    "destination": null,
    "match_score": 0.95,
    "reasoning": "Destination None aligns with your vibe."
  },
  {
    "case": "Family Friendly Nature",
    "input": {
      "preferences": {
        "family": 0.8,
        "nature": 0.7
      },
      "constraints": [
        "safety: High"
      ],
      "mood": "Safe place for kids to see animals and parks"
    },
    "status": "SUCCESS",
    "duration": "0.04s",
    "destination": null,
    "match_score": 0.95,
    "reasoning": "Destination None aligns with your vibe."
  },
  {
    "case": "Spiritual Journey",
    "input": {
      "preferences": {
        "spirituality": 0.9,
        "culture": 0.8
      },
      "constraints": [
        "budget: Budget"
      ],
      "mood": "Seeking enlightenment and ancient wisdom"
    },
    "status": "SUCCESS",
    "duration": "0.04s",
    "destination": null,
    "match_score": 0.95,
    "reasoning": "Destination None aligns with your vibe."
  },
  {
    "case": "Modern Tech Hub",
    "input": {
      "preferences": {
        "urban": 0.9,
        "technology": 0.8
      },
      "constraints": [
        "budget: Mid-range"
      ],
      "mood": "Neon lights, skyscrapers, and high-tech vibes"
    },
    "status": "SUCCESS",
    "duration": "0.05s",
    "destination": null,
    "match_score": 0.95,
    "reasoning": "Destination None aligns with your vibe."
  }
]
```
