# CityFit AI

CityFit AI is a city recommendation and GenAI advisory platform that ranks cities using Numbeo-style quality-of-life metrics, a personalized CityFit Score, and a RAG-powered agent workflow.

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

## Current MVP

The current version:

- Loads a 50-city Numbeo-derived sample dataset
- Validates the expected schema
- Engineers affordability and quality features
- Calculates a personalized CityFit Score
- Compares CityFit ranking against Numbeo's baseline Quality of Life ranking
- Serves recommendations through a FastAPI backend
- Displays rankings and explanations in a Streamlit frontend
- Supports a chat-style CityFit Agent interface
- Retrieves methodology and limitation context from a local RAG knowledge base
- Returns governance metadata, sources, tools used, and limitations
- Runs inside Docker

## Architecture

Raw city metrics CSV
  ↓
Local validation + feature engineering
  ↓
CityFit scoring logic
  ↓
FastAPI recommendation endpoints
  ↓
Streamlit frontend

GenAI/RAG flow:

User question
  ↓
Streamlit chat UI
  ↓
FastAPI /agent/query
  ↓
Chroma retriever over markdown knowledge base
  ↓
CityFit agent tools:
    - rank_city_recommendations
    - compare_cities
    - get_city_metrics
  ↓
Structured response:
    - answer
    - compared cities
    - city metrics
    - retrieved sources
    - governance metadata
    - limitations

## Run with Docker

Build the containers:

`docker compose build`

Run the ranking pipeline:

`docker compose run --rm cityfit python -m scripts.run_cityfit_ranking`

Run the FastAPI backend:

`docker compose up api`

FastAPI docs:

`http://localhost:8000/docs`

Run the Streamlit frontend:

`docker compose up api streamlit`

Streamlit app:

`http://localhost:8501`

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

## API Endpoints

### Health Check

`GET /health`

### City Recommendations

`POST /recommend`

Returns ranked city recommendations based on user priorities.

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

## Databricks Lakehouse Pipeline

The Databricks notebooks implement a medallion architecture:

- `01_ingest_bronze.py`: reads the raw CSV and writes a Bronze Delta table
- `02_clean_silver.py`: validates schema, casts types, removes duplicates, and writes a Silver Delta table
- `03_feature_engineering_gold.py`: creates affordability features, calculates CityFit Score, and writes a Gold recommendation table
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
- feature transformations
- CityFit scoring
- FastAPI endpoints
- RAG retrieval
- agent response structure and governance metadata

## Data Notice

This project uses a small educational sample derived from publicly available Numbeo city ranking pages. Numbeo data is credited to Numbeo.com and is not covered by this repository's code license.

This project does not redistribute a full Numbeo dataset or use automated scraping.

## Limitations

- The current dataset is small and intended for educational/portfolio use.
- CityFit scoring is heuristic and based on configurable weights.
- The ML model currently uses synthetic labels derived from the CityFit Score.
- The agent is currently deterministic and tool-orchestrated; it does not yet call a hosted LLM.
- Recommendations are informational and should not be treated as financial, legal, immigration, medical, or relocation advice.

## Roadmap

Planned improvements:

- Add optional LLM provider abstraction
- Add richer city/country/region filtering
- Expand the city dataset
- Add more knowledge-base documents
- Add model/provider evaluation harness
- Add optional AWS storage or deployment proof of concept
- Add screenshots and UI polish