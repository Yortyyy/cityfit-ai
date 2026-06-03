# Responsible AI Policy

CityFit AI should provide transparent, cautious, and auditable recommendations.

The system should help users compare cities, but it should not make unsupported claims or present recommendations as guaranteed outcomes.

## Responsible Use Guidelines

CityFit should:

- Explain the data used in each recommendation.
- Mention relevant limitations.
- Avoid pretending the dataset is complete.
- Avoid giving legal, financial, immigration, medical, or tax advice.
- Distinguish between baseline rankings and personalized recommendations.
- Show tradeoffs instead of only showing a single best city.
- Encourage users to verify important decisions with official or current sources.

## AI Response Requirements

AI-generated responses should include:

- The cities being compared
- The key metrics used
- The main strengths and weaknesses of each city
- The sources or knowledge-base documents used
- Any relevant limitations
- A clear statement that recommendations are informational

## Governance Metadata

Each AI response should include metadata that supports auditability.

Recommended metadata includes:

- Prompt version
- Data version
- Tools used
- Retrieved sources
- Model/provider used
- Known limitations

## Hallucination Control

The system should avoid making claims outside the available city metrics or retrieved knowledge-base context.

If the system does not have enough information, it should say so clearly.