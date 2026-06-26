# CityFit

CityFit is a city recommendation and GenAI decision-support platform that ranks cities using Numbeo-style quality-of-life metrics, a personalized CityFit Score, lifestyle metrics, and a RAG-powered agent workflow.

The project is designed to demonstrate applied AI engineering patterns:

- Python/FastAPI backend
- Streamlit frontend
- Dockerized services
- RAG over a local knowledge base
- Agent-style tool orchestration
- Chroma vector database
- MLflow + XGBoost experiment tracking
- Databricks Bronze/Silver/Gold Lakehouse notebooks
- Pytest test coverage
- GitHub Actions CI

## Demo Preview

### Interactive Globe

![CityFit interactive globe](docs/images/globe_page.PNG)

### City Profile

![CityFit city profile](docs/images/city_profile.PNG)

### City Comparison

![CityFit city comparison](docs/images/city_comparison.PNG)

### CityFit Agent

![CityFit agent response](docs/images/agent_response.PNG)

## Current MVP

The current version:

- Loads a 300+ city quality-of-life dataset with country, region, latitude, and longitude metadata
- Validates the expected city metrics schema before scoring or serving recommendations
- Calculates Practical Fit from quality-of-life, affordability, housing, safety, healthcare, climate, traffic, pollution, and purchasing-power metrics
- Calculates Lifestyle Fit from daily life, food scene, culture, outdoors, transit, airport access, and nightlife scores
- Blends Practical Fit and Lifestyle Fit into the CityFit Score through optional overall influence sliders
- Converts user-facing 0-10 Streamlit priority sliders into backend 0-2 priority multipliers
- Builds a neutral baseline CityFit ranking where all practical and lifestyle priorities are set to default importance
- Compares personalized CityFit ranking against the neutral baseline CityFit ranking
- Calculates rank movement as baseline CityFit rank minus personalized CityFit rank
- Supports region and country scoped recommendations
- Displays an interactive globe with searchable and clickable city selection
- Shows city profile pages with score summaries, metric breakdowns, flags, explanations, and similar-city links
- Supports side-by-side city comparison with rank movement, practical metrics, and lifestyle metric differences
- Serves recommendations through a FastAPI backend
- Uses a shared recommendation service so the API and agent apply the same scoring and filtering logic
- Supports a chat-style CityFit Agent interface
- Uses a local RAG knowledge base to ground agent responses in CityFit methodology, scoring assumptions, data limitations, relocation risks, and responsible-AI guidance
- Retrieves context from local markdown documents using Chroma vector search
- Returns governance metadata, retrieved sources, tools used, and limitations with agent responses
- Runs inside Docker with separate services for FastAPI, Streamlit, MLflow, and optional Ollama
- Includes pytest coverage for scoring, ranking, API behavior, city comparison logic, RAG retrieval, and agent response structure

## Architecture

Raw city metrics CSV
  -> Local validation + feature engineering
  -> Practical Fit scoring
  -> Lifestyle metric merge and Lifestyle Fit scoring
  -> Practical/Lifestyle score blending
  -> Region/country filtering
  -> FastAPI recommendation endpoints
  -> Streamlit frontend

GenAI/RAG flow:

User question
  -> Streamlit chat UI
  -> FastAPI /agent/query
  -> Chroma retriever over markdown knowledge base
  -> CityFit agent tools:
    - rank_city_recommendations
    - compare_cities
    - get_city_metrics
    - shared region/country scoped recommendation service
  -> Response provider:
    - template provider for deterministic responses
    - optional Ollama provider for local LLM-generated responses
  -> Structured response:
    - answer
    - compared cities
    - city metrics
    - retrieved sources
    - governance metadata
    - limitations

## Recommendation Service

CityFit uses a shared recommendation service so the FastAPI endpoints and agent tools rely on the same ranking pipeline.

The shared service handles:

- loading raw city metrics
- validating required schema fields
- calculating Practical Fit scores
- merging lifestyle metrics
- calculating personalized Lifestyle Fit scores
- blending Practical Fit and Lifestyle Fit into CityFit Score
- adding CityFit baseline and personalized ranks
- applying optional region and country filters
- adding human-readable city explanations where needed

This avoids separate API and agent ranking logic drifting out of sync.

## Scoring Methodology

CityFit has two score layers: Practical Fit and Lifestyle Fit. The final CityFit Score blends those layers based on the user's overall category influence sliders.

The Streamlit UI uses user-friendly 0-10 priority sliders. These are normalized before being sent to the API:

- `0` means the priority is ignored
- `5` means default importance
- `10` means double importance

Internally, the API receives these as 0-2 priority multipliers.

Practical Fit starts with Numbeo's quality-of-life index and a weighted practical priority score:

```text
practical_priority_score =
    weighted_average(
        0.15 * purchasing_power_score,
        0.10 * affordability_score,
        0.15 * safety_score,
        0.10 * healthcare_score,
        0.15 * housing_affordability_score,
        0.10 * low_traffic_score,
        0.15 * climate_score,
        0.10 * low_pollution_score
    )

practical_score =
    (
        0.30 * numbeo_quality_of_life_index
        + 0.70 * practical_priority_score
    )
    * 1.75
```

The remote-work checkbox reduces the low-traffic weight by half because commuting matters less for remote workers.

Lifestyle Fit uses free proxy metrics for lifestyle priorities:

```text
lifestyle_score =
    0.20 * daily_life_score
    + 0.15 * food_scene_score
    + 0.15 * culture_score
    + 0.15 * outdoors_score
    + 0.15 * transit_score
    + 0.10 * airport_score
    + 0.10 * nightlife_score
```

OSM-based lifestyle categories use density-adjusted counts when `land_area_km2` is available. This helps coastal, lake, river, and island cities avoid being penalized because part of the 8 km scoring radius is water instead of usable land.

The raw 0-100 Lifestyle Score is mapped onto the original CityFit scale before blending, where near 0 is a poor fit, around 100 is broadly livable, and 200+ is exceptional.

```text
cityfit_score =
    (
        practical_fit_weight * practical_score
        + lifestyle_fit_weight * lifestyle_fit_score
    )
    / total_fit_weight
```

CityFit also calculates a neutral baseline ranking where every priority is set to default importance. Personalized rank movement compares the user's personalized ranking against this neutral CityFit baseline.

## Run with Docker

Build the containers:

`docker compose build`

Run the ranking pipeline:

`docker compose run --rm api python -m scripts.update_cityfit_rank`

Run the FastAPI backend:

`docker compose up api`

FastAPI docs:

`http://localhost:8000/docs`

Run the Streamlit frontend:

`docker compose up api streamlit`

Streamlit app:

`http://localhost:8501`

Run the full app with deterministic/template responses:

`docker compose up api streamlit`

Run the full app with local Ollama available:

`docker compose up api streamlit ollama`

If using Ollama for the first time, pull a model:

`docker exec -it cityfit-ollama ollama pull llama3.1:8b`

For faster local testing, use a smaller model:

`docker exec -it cityfit-ollama ollama pull llama3.2:3b`

## RAG Knowledge Base

The RAG system retrieves from markdown documents in:

`data/knowledge_base/`

Current knowledge-base files:

- `cityfit_methodology.md`
- `data_limitations.md`
- `quality_of_life_index_notes.md`
- `relocation_risk_framework.md`
- `responsible_ai_policy.md`

Ingest the knowledge base into Chroma:

`docker compose run --rm cityfit python -m cityfit.rag.ingest`

Test retrieval:

`docker compose run --rm cityfit python -m cityfit.rag.retriever`

Generated vector database files are stored locally in:

`data/vector_store/`

This folder is ignored by Git because it is a generated artifact.

## LLM Providers

CityFit supports provider-swappable response generation.

Current providers:

- `template`: deterministic response generation with no LLM required
- `llm`: local Ollama response generation

The default mode is `template` because it is reproducible, fast, and free.

The Ollama provider can be enabled for more natural language responses while still using the same retrieved context, city metrics, and agent tools.

Supported local models can be configured through Docker environment variables:

- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`

## API Endpoints

### Health Check

`GET /health`

### City Recommendations

`POST /recommend`

Returns ranked city recommendations based on user priorities, with optional region and country filters.

### Agent Query

`POST /agent/query`

Returns an auditable agent-style response with:

- answer
- compared cities
- city results
- retrieved context
- sources
- prompt version
- data version
- tools used
- limitations

The agent respects the same region and country filters as the recommendation endpoint.

## Databricks Lakehouse Pipeline

The Databricks notebooks implement a medallion architecture:

- `01_ingest_bronze.py`: reads the raw CSV and writes a Bronze Delta table
- `02_clean_silver.py`: validates schema, casts types, removes duplicates, and writes a Silver Delta table
- `03_feature_engineering_gold.py`: calculates CityFit Score, adds ranking fields, and writes a Gold recommendation table
- `04_train_ranking_model.py`: trains an XGBoost ranking model and logs the experiment with MLflow

Tables:

- `bronze_city_quality_of_life_raw`
- `silver_city_quality_of_life_metrics`
- `gold_cityfit_recommendations`
- `gold_cityfit_model_predictions`

## MLflow + XGBoost

CityFit includes an XGBoost ranking model tracked with MLflow.

The current model uses synthetic labels derived from the CityFit Score:

`is_good_fit = 1 if city is in the top 30% by CityFit Score`

This is useful for demonstrating a supervised ML workflow, but it is not the same as training on real user behavior.

Train the local model:

`docker compose run --rm cityfit python -m cityfit.models.train_ranker`

Run local model predictions:

`docker compose run --rm cityfit python -m cityfit.models.predict`

Launch the MLflow UI:

`docker compose up mlflow`

MLflow UI:

`http://localhost:5000`

## Testing

Run all tests:

`docker compose run --rm cityfit pytest`

The test suite covers:

- schema validation
- Practical Fit scoring
- Lifestyle Fit scoring
- Practical/Lifestyle score blending
- reusable recommendation filtering
- FastAPI endpoints
- region and country scoped recommendations
- RAG retrieval
- agent response structure and governance metadata
- API/agent consistency for filtered recommendations
- deterministic CityFit ranking behavior
- baseline CityFit vs personalized CityFit rank movement
- frontend city comparison color behavior
- lifestyle metric loaders and scoring helpers

## Data Notice

This project uses an educational city dataset derived from publicly available Numbeo city ranking pages. Numbeo data is credited to Numbeo.com and is not covered by this repository's code license.

This project does not redistribute a full Numbeo dataset or use automated scraping.

## Limitations

- The current dataset is intended for educational/portfolio use and may not reflect every city or the latest real-world conditions.
- CityFit scoring is heuristic and based on configurable weights.
- Lifestyle metrics are proxy scores and do not yet include full quality, neighborhood-level, or paid review data.
- Friendliness is intentionally blank until a legally usable newcomer-integration source is chosen.
- Pace of life is categorical and is not currently blended as a higher-is-better score.
- The ML model currently uses synthetic labels derived from the CityFit Score.
- The agent supports deterministic template responses and optional local Ollama responses. Hosted LLM providers such as OpenAI, Anthropic, Gemini, or Bedrock are not yet implemented.
- Recommendations are informational and should not be treated as financial, legal, immigration, medical, or relocation advice.

## Roadmap

Planned improvements:

- Expand city detail pages with richer lifestyle summaries
- Add quality adjustments for lifestyle categories where a usable source is available
- Add a legally usable friendliness or newcomer-integration source
- Add preference matching for pace of life
- Add hosted LLM providers such as OpenAI, Anthropic, Gemini, or Bedrock
- Add response-mode evaluation for template vs Ollama outputs
- Add more knowledge-base documents
- Add model/provider evaluation harness
- Add optional AWS storage or deployment proof of concept
- Add screenshots and UI polish
