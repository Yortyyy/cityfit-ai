# CityFit Lifestyle Metrics Plan

## Goal

CityFit currently scores cities using practical quality-of-life metrics such as affordability, safety, healthcare, housing, climate, pollution, traffic, and purchasing power.

The next expansion is to add a separate Lifestyle Fit layer that captures how well a city matches a user's preferred day-to-day lifestyle.

The goal is not to replace the current CityFit Score. The goal is to make recommendations feel more personal and explainable.

---

## Design Decision

CityFit should eventually have multiple score layers:

1. **Practical Fit**

   * Based on current CityFit metrics.
   * Covers affordability, safety, healthcare, housing, traffic, pollution, climate, and purchasing power.

2. **Lifestyle Fit**

   * Based on day-to-day lifestyle preferences.
   * Covers daily-life convenience, food scene, nightlife, culture, outdoor access, transit, airport access, friendliness, and pace of life.

3. **Overall Fit**

   * Optional future combined score.
   * Combines Practical Fit and Lifestyle Fit using user-selected importance.

For now, Lifestyle Fit should be separate from the main CityFit Score.

---

## Phase 1 Scope

Phase 1 creates stable lifestyle score columns using free, source-backed proxy features.

The first method version mainly uses amenity counts, infrastructure proximity, airport proximity, and existing CityFit indicators where appropriate. Future method versions may blend quantity and quality data without changing the public score columns.

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
friendliness_score
pace_of_life
lifestyle_score
data_quality
method_version
```

The detailed calculation method should be documented separately through `method_version`, methodology notes, and optional intermediate feature columns.

Phase 1 should avoid claiming to measure full walkability, sidewalk safety, restaurant quality, nightlife quality, or neighborhood-level experience. Those may be added later through richer data sources.

---

## Proposed Lifestyle Metrics

| Metric         | Description                                                                                         | Higher Is Better? | Notes                                                                                        |
| -------------- | --------------------------------------------------------------------------------------------------- | ----------------: | -------------------------------------------------------------------------------------------- |
| Daily Life     | Access to useful everyday amenities such as groceries, cafes, pharmacies, gyms, parks, and services |               Yes | Phase 1 proxy for convenience, not full walkability                                          |
| Public Transit | Availability and usefulness of public transit infrastructure                                        |               Yes | Phase 1 can use station/stop density; later versions may include GTFS frequency and coverage |
| Outdoors       | Access to parks, beaches, trails, green space, mountains, and nature                                |               Yes | Needs careful proxy design because access is not only about POI counts                       |
| Nightlife      | Availability of bars, clubs, late-night activity, and social energy                                 |  Preference-based | Higher is good only if the user values nightlife                                             |
| Culture        | Access to museums, theatres, galleries, historic sites, music, and arts                             |               Yes | Phase 1 proxy can use cultural POI density                                                   |
| Food Scene     | Access to restaurants, cafes, bakeries, markets, and food variety                                   |               Yes | Phase 1 measures availability; quality can be added later with ratings                       |
| Airport Access | Access to meaningful domestic or international air travel                                           |               Yes | Can use distance to medium/large airports and airport importance                             |
| Friendliness   | Proxy estimate of how welcoming or socially open a place may feel                                   |               Yes | Hard to measure at city level; should include confidence/source-level labels                 |
| Pace of Life   | Whether the city feels slow, moderate, or fast-paced                                                |           Depends | Should be preference-matched, not scored as simply high or low                               |

---

## Deferred Metrics

Some metrics are useful but should not be part of Phase 1.

| Metric             | Reason to Defer                                                                                                            |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| Family Score       | May overlap too much with existing Practical Fit metrics such as safety, healthcare, affordability, pollution, and housing |
| Career Opportunity | Requires role-specific labor market data to be meaningful                                                                  |
| True Walkability   | Requires sidewalk quality, crossing safety, pedestrian infrastructure, road speeds, and neighborhood-level detail          |
| Social Scene       | Difficult to measure cleanly without subjective or platform-specific data                                                  |
| Quality Ratings    | Requires ratings/review data from sources such as Google Places, Foursquare, Yelp, or similar providers                    |

A future `family_score` should only be added if it includes family-specific data beyond the current Practical Fit metrics, such as school access, childcare availability, playground access, family activities, pediatric care, and family-sized housing practicality.

---

## Scoring Approach

Lifestyle metrics should be normalized to a 0–100 scale where possible.

Phase 1 should use stable public score columns:

```text
daily_life_score = 0 to 100
food_scene_score = 0 to 100
nightlife_score = 0 to 100
culture_score = 0 to 100
outdoors_score = 0 to 100
transit_score = 0 to 100
airport_score = 0 to 100
friendliness_score = 0 to 100
```

`pace_of_life` should initially be categorical instead of numeric:

```text
slow
moderate
fast
```

Initial Lifestyle Fit formula:

```text
lifestyle_score = weighted average of selected lifestyle scores
```

Phase 1 scores should mostly be source-backed proxy scores. For example:

```text
food_scene_score = normalized food-related POI availability
culture_score = normalized culture-related POI availability
airport_score = airport proximity and airport importance
```

Future versions may blend quantity and quality:

```text
food_scene_score =
0.50 * food_quantity_score
+ 0.50 * food_quality_score
```

However, quality fields should not be forced if the data is unavailable or weak.

---

## Quantity vs Quality

The long-term goal is to blend both quantity and quality where possible.

| Score        | Quantity Side                          | Quality Side                                       | Phase 1 Status               |
| ------------ | -------------------------------------- | -------------------------------------------------- | ---------------------------- |
| Food Scene   | Number and density of food venues      | Ratings and review counts                          | Quantity only                |
| Nightlife    | Number and density of nightlife venues | Ratings and review counts                          | Quantity only                |
| Culture      | Number and density of cultural venues  | Ratings, prominence, and review counts             | Quantity only                |
| Daily Life   | Availability of everyday amenities     | Ratings/usefulness of amenities                    | Quantity only                |
| Outdoors     | Parks, trails, beaches, green spaces   | Size, quality, ratings, maintenance, natural value | Quantity/proximity only      |
| Transit      | Stops, stations, route access          | Frequency, reliability, span, speed                | Basic access proxy           |
| Airport      | Distance to airports and airport size  | Connectivity/passenger volume                      | Basic airport proxy          |
| Friendliness | Survey/social indicators               | City-level sentiment or expat experience           | Country or survey proxy only |

For Phase 1, quality-related columns can be left out of the public CSV or kept as internal nullable fields. The app should not present quality-adjusted scores until quality data is actually available.

Current airport scoring uses a source-backed proxy rather than true airport quality:

```text
airport_score =
    distance/proximity score
    adjusted by route connectivity
    adjusted by passenger volume when known
```

The distance component comes from OurAirports medium and large scheduled airports. Route connectivity comes from OpenFlights direct-route counts, which are useful as a global proxy but should be treated as historical because OpenFlights route updates stopped in 2014. Passenger volume currently comes from the busiest-airports passenger traffic table where an airport can be matched by IATA or ICAO code, so coverage is strongest for major global hubs and missing for many smaller airports.

Airports marked as not currently scheduled in OurAirports can still be included when they have route-connectivity or passenger-volume evidence. This prevents structurally important airports from being scored as nonexistent when service is suspended or the scheduled-service flag is stale.

Current daily-life scoring is also a source-backed proxy rather than a true neighborhood convenience or walkability score:

```text
daily_life_score =
    grocery and market availability
    + pharmacy availability
    + cafe and casual food availability
    + fitness availability
    + park and garden availability
    + basic services availability
    + clinic, doctor, and dentist availability
```

The current method uses OpenStreetMap node counts within 8 km of each city coordinate. It intentionally counts availability near the city center, not sidewalk quality, opening hours, venue ratings, or neighborhood-level access. OpenStreetMap coverage varies by country and city, so the score should remain labeled as a Phase 1 proxy.

Current food-scene scoring reuses the same OpenStreetMap amenity cache:

```text
food_scene_score =
    restaurant, cafe, and fast-food availability
    + food shop and market availability
```

Restaurants, cafes, and fast food carry most of the weight. Food shops and markets provide a smaller supporting signal. The score does not yet measure ratings, cuisine diversity, price range, reservation difficulty, critic coverage, or local reputation.

Current nightlife scoring uses a separate OpenStreetMap nightlife cache:

```text
nightlife_score =
    bar and pub availability
    + nightclub availability
    + music and live-venue availability
    + late-entertainment availability
```

Bars and pubs carry the largest share because they are the most consistently mapped nightlife signal across countries. Nightclubs, music venues, and late-entertainment amenities add stronger social-energy signals where they are present. The score measures mapped nightlife POIs within 8 km of the city coordinate. It does not yet measure opening hours, venue quality, event frequency, crowd size, safety, local reputation, or whether a city's nightlife is concentrated in specific neighborhoods.

Current culture scoring uses a separate OpenStreetMap culture cache:

```text
culture_score =
    museum availability
    + performing arts venue availability
    + gallery and public artwork availability
    + cinema availability
    + historic site availability
```

The score measures mapped cultural-place availability within 8 km of the city coordinate. It does not yet measure venue quality, collection importance, event frequency, ticket access, language accessibility, or whether the city has a strong contemporary arts scene beyond what is mapped in OpenStreetMap.

Current transit scoring uses a separate OpenStreetMap transit cache:

```text
transit_score =
    bus stop availability
    + rail and train station availability
    + metro, subway, tram, and light rail availability
    + ferry terminal and aerialway station availability
    + major transit hub availability
```

This includes mapped buses, trains, metro/subway, trams/light rail/trolleys where represented in OSM transit infrastructure, ferry terminals, and aerialway stations such as cable cars or gondolas. It measures mapped access points within 8 km of the city coordinate. It does not yet measure route frequency, service span, reliability, fares, travel speed, crowding, network coverage by neighborhood, or GTFS schedule quality.

Current outdoors scoring uses a separate OpenStreetMap outdoors cache:

```text
outdoors_score =
    park, garden, and recreation-ground availability
    + nature reserve and protected-area availability
    + mapped trail and route-marker availability
    + beach, marina, and water-recreation availability
    + viewpoint and peak availability
```

The current method measures mapped outdoor access points within 8 km of the city coordinate. It does not yet measure park size, tree canopy, waterfront length, trail quality, mountain access beyond the city radius, safety, maintenance, crowding, beach quality, or climate. Outdoors scores are especially sensitive to OpenStreetMap tagging coverage because many outdoor amenities are mapped as large ways/relations rather than simple points.

Current pace-of-life classification uses a culture/work-life proxy score and then converts it to a preference label:

```text
pace_intensity =
    country or regional cultural pace baseline
    + light commute-pressure adjustment
    + light nightlife-activity adjustment

pace_of_life =
    slow | moderate | fast
```

Pace of life is not treated as a higher-is-better score. A faster city is not inherently better than a slower city; the label is meant to match user preference. Phase 1 prioritizes local cultural and work-life rhythm over density or amenity volume, so a dense city can still be labeled slow when the day-to-day rhythm is more relaxed. Existing CityFit traffic data and nightlife activity can nudge the label, but they should not overwhelm the cultural baseline. It does not yet include direct working-hours data, time-use surveys, local business closing times, pedestrian speed, or subjective resident sentiment.

Friendliness scoring is deferred until CityFit has a legally usable source that directly measures newcomer integration and warmth to strangers:

```text
friendliness_score =
    pending
```

The intended meaning is estimated ease of social integration for a newcomer, including warmth toward strangers, ease of making local friends, openness to outsiders, language/social accessibility, and whether everyday interactions feel welcoming. It should not be a general happiness score and should not be presented as a definitive statement about individual people.

This metric should remain blank until the data source is both methodologically appropriate and legally reusable. Social-support datasets such as World Happiness Report or OECD community indicators may be useful supporting inputs, but they do not directly measure warmth to strangers or newcomer integration. Expat/newcomer surveys may be a closer fit, but their licensing and reuse rights must be verified before storing their rankings or derived scores in CityFit.

---

## Data Strategy

### Phase 1: Free Source-Backed Proxy Data

Start with free and source-backed proxy data.

Possible sources:

* OpenStreetMap for amenities, transit stops, parks, cultural venues, food venues, and nightlife venues
* OurAirports for airport location and airport type
* Existing CityFit data for practical indicators where relevant
* Legally reusable survey data for friendliness/newcomer-integration proxy when available

Phase 1 output:

```text
data/reference/lifestyle_metrics.csv
```

Example columns:

```csv
city,state,country,region,latitude,longitude,daily_life_score,food_scene_score,nightlife_score,culture_score,outdoors_score,transit_score,airport_score,friendliness_score,pace_of_life,lifestyle_score,data_quality,method_version
Tampa,United States,North America,27.95,-82.45,,,,,,,,,,,medium,free_proxy_v1
Rome,Italy,Europe,41.9028,12.4964,,,,,,,,,,,medium,free_proxy_v1
Tokyo,Japan,Asia,35.6762,139.6503,,,,,,,,,,,medium,free_proxy_v1
```

### Phase 2: Quality Adjustment

Later, add quality data where it is available and worth the cost.

Possible additions:

* Google rating and user rating count
* Foursquare or similar venue-quality data
* GTFS transit frequency and coverage
* Airport passenger volume or route connectivity
* Better country/city survey data for friendliness

Phase 2 should preserve the same public columns while improving how the scores are calculated.

---

## UI Placement

Lifestyle Fit should appear separately from the current practical metric breakdown.

Possible layout:

```text
Lifestyle Fit
- Daily Life
- Food Scene
- Nightlife
- Culture
- Outdoors
- Transit
- Airport Access
- Friendliness
- Pace of Life
```

The UI should make it clear that Lifestyle Fit is a separate layer from the current CityFit Score.

---

## Agent Usage

The CityFit agent should eventually answer questions like:

```text
Which city has the best food scene?
Which city fits a slower lifestyle?
Which city is better for nightlife?
Why is Rome a better lifestyle fit than Tampa?
Find cities with strong outdoor access and reasonable cost of living.
Which cities feel more friendly or welcoming?
```

The agent should explain Lifestyle Fit separately from Practical Fit.

---

## First Implementation Plan

1. Create `data/reference/lifestyle_metrics.csv`
2. Add a loader for lifestyle metrics
3. Merge lifestyle metrics onto ranked city data by city + country
4. Add `lifestyle_score`
5. Display Lifestyle Fit in City Profile
6. Add Lifestyle Fit to city comparison
7. Teach the agent to explain lifestyle strengths and tradeoffs

---

## Risks / Limitations

Lifestyle data is more subjective than practical quality-of-life data.

Potential issues:

* Scores may be incomplete for some cities
* OpenStreetMap coverage varies by country and city
* Quantity does not always equal quality
* Some scores are proxies, not definitive measurements
* Friendliness is especially difficult to measure at the city level
* Neighborhood-level lifestyle may differ greatly from city-level averages
* Some metrics are preference-based instead of universally good or bad

CityFit should clearly label Lifestyle Fit as an estimate and include `data_quality` and `method_version` fields.
