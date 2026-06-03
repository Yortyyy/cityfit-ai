# Data Limitations

CityFit AI currently uses a small educational sample derived from publicly available city quality-of-life ranking data.

The dataset is suitable for demonstration, prototyping, and portfolio purposes. It is not a complete commercial relocation dataset.

## Current Limitations

The current dataset has several limitations:

- It contains a limited number of cities.
- Some values may represent point-in-time snapshots.
- City-level metrics may not capture neighborhood-level differences.
- The dataset may not reflect recent price, safety, healthcare, or housing changes.
- Some metrics are based on aggregated user-contributed or externally reported data.
- The current model does not use real user feedback labels.

## Synthetic ML Labels

The current XGBoost ranking model uses synthetic labels derived from the CityFit Score.

For example, a city may be labeled as a good fit if it falls in the top 30 percent of CityFit Scores.

This is useful for demonstrating an ML workflow, but it is not the same as training on real user behavior.

In a production system, better labels could come from:

- Saved cities
- User ratings
- Click behavior
- Survey responses
- Relocation outcomes
- Long-term satisfaction feedback

## Recommendation Limits

CityFit recommendations should not be treated as financial, legal, immigration, medical, or relocation advice.

The system is intended to help users compare cities and understand tradeoffs.

Users should verify important decisions with official sources and current local information.