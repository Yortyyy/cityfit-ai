# CityFit Methodology

CityFit AI is a city recommendation system that compares cities using quality-of-life, affordability, safety, healthcare, climate, pollution, traffic, and purchasing-power metrics.

The project uses Numbeo-style city metrics then creates a fitted baseline to priorities set equal to one another and then applies a personalized CityFit Score based on user changed priority scalings.

## Baseline Ranking

The baseline ranking comes from the CityFit priority set equal to 5 out of 10 for all priorities. This index is not treated as the final recommendation.

## Personalized CityFit Score

The CityFit Score combines positive factors and penalty factors.

Positive factors include:

- CityFit Score
- Purchasing Power Index
- Safety Index
- Healthcare Index
- Climate Index

Penalty factors include:

- Cost of Living Index
- Property Price to Income Ratio
- Pollution Index
- Traffic Commute Index

A higher CityFit Score means a city better matches the selected user priorities.

## Personalization

User priorities adjust the weight of each factor.

For example:

- A remote worker may care less about commute time.
- A family may prioritize safety and healthcare.
- A cost-sensitive user may prioritize affordability.
- A climate-focused user may prioritize climate and pollution.

The same city can rank differently depending on the user's profile.

## Rank Difference

CityFit compares the personalized CityFit ranking against the baseline Cityfit ranking.

A positive rank difference means the city ranks higher under CityFit personalization than it does under the baseline ranking.

A negative rank difference means the city ranks lower under CityFit personalization than it does under the baseline ranking.

## Recommendation Philosophy

CityFit is designed to support decision-making, not replace it.

The system should explain tradeoffs clearly and avoid presenting recommendations as absolute truth.
