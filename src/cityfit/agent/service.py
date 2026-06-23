from cityfit.agent.prompts import AGENT_PROMPT_VERSION
from cityfit.agent.tools import (
    compare_cities,
    explain_city_fit,
    extract_city_names,
    get_available_cities,
    rank_city_recommendations,
)
from cityfit.api.schemas import UserProfile
from cityfit.llm.provider import get_llm_provider
from cityfit.rag.retriever import retrieve_context

"""
CityFit agent routing order:

1. City explanation questions
   Example: "Why is Tampa ranked where it is?"
   Tool: explain_city_fit

2. Methodology questions
   Example: "How does CityFit calculate scores?"
   Tool: retrieve_context

3. City comparison questions
   Example: "Compare Tampa and Rome."
   Tool: compare_cities

4. General recommendation questions
   Example: "What cities are best for my profile?"
   Tool: rank_city_recommendations
"""


DATA_VERSION = "numbeo_2026_sample_v1"

METHODOLOGY_KEYWORDS = [
    "methodology",
    "how does cityfit work",
    "how cityfit works",
    "how is cityfit calculated",
    "how are scores calculated",
    "score",
    "scoring",
    "rank movement",
    "baseline",
    "weights",
    "limitations",
    "data source",
    "quality of life",
    "responsible ai",
]

WHY_CITY_KEYWORDS = [
    "why",
    "explain",
    "ranked",
    "rank",
    "score",
    "good fit",
    "bad fit",
    "hurts",
    "hurt",
    "helps",
    "help",
    "strengths",
    "weaknesses",
    "moved up",
    "moved down",
]


def _is_methodology_question(question: str) -> bool:
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in METHODOLOGY_KEYWORDS)


def _format_bullets(items: list[str], fallback: str) -> str:
    if not items:
        return f"- {fallback}"

    return "\n".join(f"- {item.capitalize()}" for item in items)


def _is_why_city_question(question: str, requested_cities: list[str]) -> bool:
    if not requested_cities:
        return False

    question_lower = question.lower()
    return any(keyword in question_lower for keyword in WHY_CITY_KEYWORDS)


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
            f"traffic {city['traffic_commute_index']:.1f}"
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
    
    city_results = []

    if _is_why_city_question(question, requested_cities):
        city_explanation = explain_city_fit(
            requested_cities[0],
            profile,
        )

        if city_explanation:
            tools_used.append("explain_city_fit")
            answer = _build_city_explanation_answer(city_explanation)
        else:
            answer = (
                f"I could not find {requested_cities[0]} in the current CityFit dataset."
            )

    elif _is_methodology_question(question):
        answer = _build_methodology_answer(retrieved_chunks)

    elif requested_cities:
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
    
def _build_methodology_answer(retrieved_chunks: list) -> str:
    metrics = [
        "Purchasing power",
        "Cost of living",
        "Safety",
        "Healthcare",
        "Housing affordability",
        "Traffic",
        "Climate",
        "Pollution",
    ]

    metric_lines = [f"- {metric}" for metric in metrics]

    lines = [
        "## Summary",
        "",
        (
            "CityFit ranks cities by combining source quality-of-life city data "
            "with a personalized scoring layer based on the user's selected priorities."
        ),
        "",
        "## How CityFit scoring works",
        "",
        (
            "CityFit starts with a default scoring baseline where each priority is treated "
            "as moderately important. When a user changes their priorities, CityFit recalculates "
            "each city's score using the same city metrics but different priority weights."
        ),
        "",
        "The current CityFit score uses these factors:",
        "",
        *metric_lines,
        "",
        (
            "The priority adjustment is normalized by total priority weight so that default "
            "and personalized scores remain comparable."
        ),
        "",
        "## Baseline vs Personalized Ranking",
        "",
        (
            "The dashboard compares a default CityFit baseline against the user's personalized "
            "CityFit ranking."
        ),
        "",
        "`rank_movement = baseline_cityfit_rank - personalized_cityfit_rank`",
        "",
        (
            "A positive rank movement means a city moved up after personalization. "
            "A negative rank movement means it moved down compared with the default CityFit baseline."
        ),
        "",
        "## Future Lifestyle Fit layer",
        "",
        (
            "Future versions of CityFit can add a separate Lifestyle Fit layer for subjective "
            "day-to-day preferences such as walkability, transit access, outdoor access, nightlife, "
            "culture, food scene, airport access, career opportunity, social scene, and pace of life."
        ),
        "",
        "## Limitations",
        "",
        (
            "CityFit is a decision-support tool. Rankings depend on the available city data, "
            "the scoring assumptions, and the user's selected priorities. Results should be used "
            "as a starting point for comparison, not as final relocation advice."
        ),
    ]

    return "\n".join(lines)


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
        rank_gap = int(city["rank_difference"])

        if rank_gap > 0:
            rank_note = f"moves up {rank_gap} spots versus the CityFit baseline"
        elif rank_gap < 0:
            rank_note = f"moves down {abs(rank_gap)} spots versus the CityFit baseline"
        else:
            rank_note = "stays aligned with its CityFit baseline rank"

        lines.extend(
            [
                f"### {city['city']}, {city['country']}",
                "",
                "**Key metrics**",
                f"- CityFit rank: **{int(city['cityfit_rank'])}**",
                f"- CityFit score: **{city['cityfit_score']:.2f}**",
                f"- Rank movement: **{rank_note}**",
                f"- Cost of living: **{city['cost_of_living_index']:.1f}**",
                f"- Purchasing power: **{city['purchasing_power_index']:.1f}**",
                f"- Safety: **{city['safety_index']:.1f}**",
                f"- Healthcare: **{city['healthcare_index']:.1f}**",
                f"- Traffic: **{city['traffic_commute_index']:.1f}**",
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
                f"- Traffic: **{city['traffic_commute_index']:.1f}**",
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
        "cityfit_rank",
        "baseline_cityfit_rank",
        "rank_difference",
        "numbeo_quality_of_life_index",
        "cityfit_score",
        "baseline_cityfit_score",
        "cost_of_living_index",
        "purchasing_power_index",
        "safety_index",
        "healthcare_index",
        "traffic_commute_index",
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


def _format_rank_movement(
    city: str,
    rank_difference: int | float | None,
) -> tuple[str, str]:
    if rank_difference is None:
        return (
            "No rank movement data",
            (
                f"{city}'s personalized rank could not be compared with the "
                "baseline CityFit rank because rank movement data is unavailable."
            ),
        )

    if rank_difference > 0:
        return (
            f"⬆️ Up {int(rank_difference)} spots",
            (
                f"{city} ranks better for your selected priorities than it does "
                "over the baseline CityFit rank."
            ),
        )

    if rank_difference < 0:
        return (
            f"⬇️ Down {abs(int(rank_difference))} spots",
            (
                f"{city} ranks lower for your selected priorities than it does "
                "under the baseline CityFit rank."
            ),
        )

    return (
        "➖ No movement",
        (
            f"{city}'s personalized rank is about the same as its baseline "
            "CityFit rank."
        ),
    )


def _build_city_explanation_answer(city_explanation: dict) -> str:
    city = city_explanation["city"]
    country = city_explanation["country"]

    rank_difference = city_explanation.get("rank_difference", 0)

    movement_label, quick_take = _format_rank_movement(city, rank_difference)

    strengths_text = _format_bullets(
        city_explanation.get("strengths", []),
        "No standout strengths were identified from the available metrics.",
    )

    tradeoffs_text = _format_bullets(
        city_explanation.get("tradeoffs", []),
        "No major tradeoffs stand out from the available metrics.",
    )

    return f"""
## {city}, {country}

**Quick take:** {quick_take}

| CityFit metric | Result |
|---|---:|
| Personalized rank | #{city_explanation["cityfit_rank"]} |
| Personalized score | {city_explanation["cityfit_score"]:.1f} |
| Baseline rank | #{city_explanation["baseline_cityfit_rank"]} |
| Baseline score | {city_explanation["baseline_cityfit_score"]:.1f} |
| Rank movement | {movement_label} |

### Strengths

{strengths_text}

### Tradeoffs

{tradeoffs_text}

### Explanation

{city_explanation["explanation"]}
""".strip()