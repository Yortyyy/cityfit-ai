# Relocation Risk Framework

CityFit AI evaluates cities using a simple relocation risk framework.

The purpose is to make city recommendations easier to understand and more transparent.

## Main Risk Categories

### Affordability Risk

Affordability risk increases when a city has a high cost of living, high property price to income ratio, or low purchasing power.

Relevant metrics:

- Cost of Living Index
- Property Price to Income Ratio
- Purchasing Power Index

### Safety and Health Risk

Safety and health risk increases when safety or healthcare scores are low.

Relevant metrics:

- Safety Index
- Healthcare Index

### Environmental Risk

Environmental risk increases when pollution is high or climate fit is poor.

Relevant metrics:

- Pollution Index
- Climate Index

### Mobility Risk

Mobility risk increases when commute time or traffic burden is high.

Relevant metric:

- Traffic Commute Index

For remote workers, traffic receives a lower penalty because daily commuting may be less important.

## Tradeoff-Based Recommendations

A city may score well overall while still having weaknesses.

For example:

- A city may have excellent quality of life but high cost.
- A city may be affordable but have weaker healthcare.
- A city may have strong safety but poor climate.
- A city may have strong purchasing power but high traffic.

CityFit should explain these tradeoffs instead of only returning a ranked list.