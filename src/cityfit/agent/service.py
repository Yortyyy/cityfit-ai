from cityfit.agent.prompts import AGENT_PROMPT_VERSION
from cityfit.agent.tools import (
    compare_cities,
    extract_city_names,
    get_available_cities,
    rank_city_recommendations,
)
from cityfit.api.schemas import UserProfile
from cityfit.llm.provider import get_llm_provider
from cityfit.rag.retriever import retrieve_context


DATA_VERSION = "numbeo_2026_sample_v1"


def _build_llm_prompt(
    question: str,
    draft_answer: str,
    sources: list[str],
    city_results: list[dict],
) -> str:
    city_summary = "\n".join(
        [
            f"- {city['city']}, {city['country']}: "
            f"CityFit rank {int(city['cityfit_rank'])}, "
            f"score {city['cityfit_score']:.2f}, "
            f"cost {city['cost_of_living_index']:.1f}, "
            f"safety {city['safety_index']:.1f}, "
            f"healthcare {city['healthcare_index']:.1f}"
            f"climate {city['climate_index']:.1f}"
            f"pollution {city['pollution_index']:.1f}"
            for city in city_results[:10]
        ]
    )

    return f"""
You are CityFit AI, a grounded city recommendation assistant.

Answer the user's question using only the provided CityFit metrics and retrieved project context.

User question:
{question}

Draft structured answer:
{draft_answer}

City metrics:
{city_summary}

Retrieved sources:
{", ".join(sources)}

Rules:
- Do not invent lifestyle, visa, neighborhood, job market, or current-event details.
- Clearly explain tradeoffs.
- Mention limitations if the available data is incomplete.
- Keep the answer concise and practical.
"""

def build_agent_answer(
    question: str,
    profile: UserProfile,
    top_k_context: int = 4,
    response_mode: str = "template",
) -> dict:
    """
    Build an auditable CityFit agent response.

    This version uses deterministic orchestration instead of an LLM:
    - retrieve RAG context
    - detect requested cities
    - call structured CityFit tools
    - return answer, sources, and governance metadata
    """
    retrieved_chunks = retrieve_context(question, top_k=top_k_context)

    available_cities = get_available_cities(profile)
    requested_cities = extract_city_names(question, available_cities)

    tools_used = ["retrieve_context"]

    if requested_cities:
        city_results = compare_cities(requested_cities, profile)
        tools_used.append("compare_cities")
        answer = _build_comparison_answer(question, city_results)
    else:
        city_results = rank_city_recommendations(profile, top_n=profile.top_n)
        tools_used.append("rank_city_recommendations")
        answer = _build_ranking_answer(question, city_results)

    sources = sorted({chunk.source for chunk in retrieved_chunks})

    provider = get_llm_provider(response_mode)

    if response_mode == "llm":
        llm_prompt = _build_llm_prompt(
            question=question,
            draft_answer=answer,
            sources=sources,
            city_results=city_results,
        )
        llm_response = provider.generate(llm_prompt)
        final_answer = llm_response.text
    else:
        llm_response = provider.generate(answer)
        final_answer = llm_response.text

    return {
        "answer": final_answer,
        "cities_compared": requested_cities,
        "city_results": _clean_city_results(city_results),
        "sources": sources,
        "retrieved_context": [
            {
                "source": chunk.source,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "distance": chunk.distance,
            }
            for chunk in retrieved_chunks
        ],
        "metadata": {
            "prompt_version": AGENT_PROMPT_VERSION,
            "data_version": DATA_VERSION,
            "tools_used": tools_used,
            "model_provider": llm_response.provider,
            "model_name": llm_response.model,
            "limitations": [
                "Uses a small educational city dataset.",
                "CityFit scoring is heuristic and user-priority based.",
                "The ML model currently uses synthetic labels.",
                "Recommendations are informational and should be verified with current official sources.",
            ],
        },
    }


def _build_comparison_answer(question: str, city_results: list[dict]) -> str:
    if not city_results:
        return (
            "I could not find matching cities in the CityFit dataset. "
            "Try asking about cities included in the current sample dataset."
        )

    best_city = min(city_results, key=lambda city: city["cityfit_rank"])

    lines = [
        "## Summary",
        "",
        (
            f"Among the requested cities, **{best_city['city']}, {best_city['country']}** "
            f"is the strongest CityFit match with a score of **{best_city['cityfit_score']:.2f}**."
        ),
        "",
        "## City comparison",
        "",
    ]

    for city in city_results:
        rank_gap = int(city["numbeo_qol_rank"] - city["cityfit_rank"])

        if rank_gap > 0:
            rank_note = f"moves up {rank_gap} spots versus the Numbeo baseline"
        elif rank_gap < 0:
            rank_note = f"moves down {abs(rank_gap)} spots versus the Numbeo baseline"
        else:
            rank_note = "stays aligned with its Numbeo baseline rank"

        lines.extend(
            [
                f"### {city['city']}, {city['country']}",
                "",
                "**Ranking**",
                f"- CityFit rank: **{int(city['cityfit_rank'])}**",
                f"- Rank movement: **{rank_note}**",
                "",
                "**Key metrics**",
                f"- CityFit score: **{city['cityfit_score']:.2f}**",
                f"- Cost of living: **{city['cost_of_living_index']:.1f}**",
                f"- Purchasing power: **{city['purchasing_power_index']:.1f}**",
                f"- Safety: **{city['safety_index']:.1f}**",
                f"- Healthcare: **{city['healthcare_index']:.1f}**",
                f"- Climate: **{city['climate_index']:.1f}**",
                f"- Pollution: **{city['pollution_index']:.1f}**",
                "",
                "**Takeaway**",
                city.get("explanation", "No explanation available."),
                "",
            ]
        )

    lines.extend(
        [
            "## Limitation",
            "",
            (
                "This comparison is based only on the current CityFit metrics. It does not include "
                "neighborhood-level lifestyle, job market, visa, tax, housing availability, or real-time local data."
            ),
        ]
    )

    return "\n".join(lines)


def _build_ranking_answer(question: str, city_results: list[dict]) -> str:
    if not city_results:
        return "I could not generate city recommendations from the current dataset."

    top_city = city_results[0]

    lines = [
        "## Summary",
        "",
        (
            f"Based on the current CityFit profile, **{top_city['city']}, {top_city['country']}** "
            "is the top recommendation."
        ),
        "",
        "## Top recommendations",
        "",
    ]

    for city in city_results[:5]:
        lines.extend(
            [
                f"### {city['city']}, {city['country']}",
                f"- CityFit rank: **{int(city['cityfit_rank'])}**",
                f"- CityFit score: **{city['cityfit_score']:.2f}**",
                f"- Purchasing power: **{city['purchasing_power_index']:.1f}**",
                f"- Cost of living: **{city['cost_of_living_index']:.1f}**",
                f"- Safety: **{city['safety_index']:.1f}**",
                f"- Healthcare: **{city['healthcare_index']:.1f}**",
                f"- Climate: **{city['climate_index']:.1f}**",
                f"- Pollution: **{city['pollution_index']:.1f}**",
                "",
                f"**Takeaway:** {city.get('explanation', 'No explanation available.')}",
                "",
            ]
        )

    lines.extend(
        [
            "## Limitation",
            "",
            (
                "These results are based on a small educational dataset and should be treated as "
                "decision support, not final relocation advice."
            ),
        ]
    )

    return "\n".join(lines)


def _clean_city_results(city_results: list[dict]) -> list[dict]:
    """
    Keep API response compact and JSON-safe.
    """
    output_columns = [
        "city",
        "country",
        "region",
        "numbeo_qol_rank",
        "cityfit_rank",
        "rank_difference",
        "numbeo_quality_of_life_index",
        "cityfit_score",
        "cost_of_living_index",
        "purchasing_power_index",
        "safety_index",
        "healthcare_index",
        "pollution_index",
        "climate_index",
        "explanation",
    ]

    cleaned = []

    for row in city_results:
        cleaned.append(
            {
                key: row[key]
                for key in output_columns
                if key in row
            }
        )

    return cleaned