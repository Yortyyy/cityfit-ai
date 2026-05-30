# CityFit AI

CityFit AI ranks cities using Numbeo quality-of-life metrics and a personalized CityFit Score based on cost of living, safety, healthcare, climate, pollution, traffic, and purchasing power.

## Current MVP

The current version:

- Loads a 50-city Numbeo-derived sample dataset
- Validates the expected schema
- Engineers affordability and quality features
- Calculates a personalized CityFit Score
- Compares CityFit ranking against Numbeo's baseline Quality of Life ranking
- Runs inside Docker

## Run with Docker

```bash
docker compose build
docker compose run --rm cityfit python -m scripts.run_cityfit_ranking