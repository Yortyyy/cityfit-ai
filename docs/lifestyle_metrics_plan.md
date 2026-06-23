# CityFit Lifestyle Metrics Plan

## Goal

CityFit currently scores cities using practical quality-of-life metrics such as affordability, safety, healthcare, housing, climate, pollution, traffic, and purchasing power.

The next expansion is to add a separate Lifestyle Fit layer that captures how well a city matches a user's preferred day-to-day lifestyle.

The goal is not to replace the current CityFit Score. The goal is to make recommendations feel more personal and explainable.

---

## Design Decision

CityFit should eventually have multiple score layers:

1. **Practical Fit**
   - Based on current CityFit metrics.
   - Covers affordability, safety, healthcare, housing, traffic, pollution, climate, and purchasing power.

2. **Lifestyle Fit**
   - Based on subjective/day-to-day fit.
   - Covers walkability, transit, outdoor access, nightlife, culture, food scene, airport access, career opportunity, social scene, and pace of life.

3. **Overall Fit**
   - Optional future combined score.
   - Combines Practical Fit and Lifestyle Fit using user-selected importance.

For now, Lifestyle Fit should be separate from the main CityFit Score.

---

## Phase 1 Scope

Phase 1 creates stable lifestyle score columns using free source-backed proxy features.

The first method version mainly uses amenity counts, infrastructure proximity, and existing CityFit indicators. Future method versions may blend quantity and quality data without changing the public score columns.

This means the app-facing columns should stay stable even if the calculation method improves later.

Example stable columns:

```text
daily_life_score
food_scene_score
nightlife_score
culture_score
outdoors_score
transit_score
airport_score
family_score
friendliness_score
pace_of_life
lifestyle_score
data_quality
method_version
```

---

## Proposed Lifestyle Metrics

| Metric | Description | Higher Is Better? | Notes |
| --- | --- |--- :|--- |
| Walkability | How easy it is to live without relying heavily on a car | Yes | Could use Walk Score or proxy data |
| Public Transit | Quality and usefulness of transit systems | Yes | Important for urban lifestyle fit |
| Outdoor Access | Access to parks, beaches, mountains, trails, and nature | Yes | Needs city-level approximation |
| Nightlife | Bars, clubs, late-night activity, and social energy | Yes | Subjective; likely heuristic at first |
| Culture | Museums, music, history, arts, events, and local identity | Yes | Could be manually curated initially |
| Food Scene | Restaurant variety and quality | Yes | Subjective; can start as curated score |
| Airport Access | Airport quality and international connectivity | Yes | Useful for remote workers/travelers |
| Career Opportunity | Strength of local job market or industry presence | Yes | Could later be role-specific |
| Social Scene | Ease of meeting people and community activity | Yes | Hard to source cleanly |
| Family Friendliness | Schools, safety, parks, stability, family infrastructure | Yes | May overlap with safety/housing |
| Pace of Life | Slow, moderate, or fast lifestyle | Depends | Should be preference-matched, not simply high/low |

---

## Scoring Approach

Lifestyle metrics should be normalized to a 0–100 scale.

Example:

```text
walkability_score = 0 to 100
transit_score = 0 to 100
outdoor_access_score = 0 to 100
nightlife_score = 0 to 100
culture_score = 0 to 100
food_scene_score = 0 to 100
airport_access_score = 0 to 100
career_score = 0 to 100
