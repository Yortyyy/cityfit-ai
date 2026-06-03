# CityFit Methodology

CityFit AI is a city recommendation system that compares cities using quality-of-life, affordability, safety, healthcare, climate, pollution, traffic, and purchasing-power metrics.

The project uses Numbeo-style city metrics as a baseline and then applies a personalized CityFit Score based on user priorities.

## Baseline Ranking

The baseline ranking comes from the Numbeo Quality of Life Index. This index is treated as an external benchmark, not as the final recommendation.

CityFit does not claim that Numbeo's ranking is incorrect. Instead, CityFit adjusts recommendations based on individual user preferences.

## Personalized CityFit Score

The CityFit Score combines positive factors and penalty factors.

Positive factors include:

- Numbeo Quality of Life Index
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

CityFit compares the personalized CityFit ranking against the baseline Numbeo Quality of Life ranking.

A positive rank difference means the city ranks higher under CityFit personalization than it does under the baseline ranking.

A negative rank difference means the city ranks lower under CityFit personalization than it does under the baseline ranking.

## Recommendation Philosophy

CityFit is designed to support decision-making, not replace it.

The system should explain tradeoffs clearly and avoid presenting recommendations as absolute truth.