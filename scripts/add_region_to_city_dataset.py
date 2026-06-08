from pathlib import Path

import pandas as pd


INPUT_PATH = Path("data/raw/numbeo_quality_of_life_city_current_dataset_2_with_osaka.csv")
OUTPUT_PATH = Path("data/raw/numbeo_quality_of_life_city_current_dataset_2_with_region.csv")


COUNTRY_TO_REGION = {
    # North America / Caribbean / Central America
    "United States": "North America",
    "Canada": "North America",
    "Mexico": "North America",
    "Costa Rica": "North America",
    "Panama": "North America",
    "Dominican Republic": "North America",
    "Puerto Rico": "North America",

    # South America
    "Argentina": "South America",
    "Brazil": "South America",
    "Chile": "South America",
    "Colombia": "South America",
    "Ecuador": "South America",
    "Peru": "South America",
    "Uruguay": "South America",
    "Venezuela": "South America",

    # Europe
    "Albania": "Europe",
    "Austria": "Europe",
    "Belarus": "Europe",
    "Belgium": "Europe",
    "Bosnia And Herzegovina": "Europe",
    "Bulgaria": "Europe",
    "Croatia": "Europe",
    "Cyprus": "Europe",
    "Czech Republic": "Europe",
    "Denmark": "Europe",
    "Estonia": "Europe",
    "Finland": "Europe",
    "France": "Europe",
    "Germany": "Europe",
    "Greece": "Europe",
    "Hungary": "Europe",
    "Iceland": "Europe",
    "Ireland": "Europe",
    "Italy": "Europe",
    "Latvia": "Europe",
    "Lithuania": "Europe",
    "Luxembourg": "Europe",
    "Moldova": "Europe",
    "Netherlands": "Europe",
    "North Macedonia": "Europe",
    "Norway": "Europe",
    "Poland": "Europe",
    "Portugal": "Europe",
    "Romania": "Europe",
    "Russia": "Europe",
    "Serbia": "Europe",
    "Slovakia": "Europe",
    "Slovenia": "Europe",
    "Spain": "Europe",
    "Sweden": "Europe",
    "Switzerland": "Europe",
    "Ukraine": "Europe",
    "United Kingdom": "Europe",

    # Asia
    "Armenia": "Asia",
    "Azerbaijan": "Asia",
    "Bangladesh": "Asia",
    "China": "Asia",
    "Georgia": "Asia",
    "Hong Kong (China)": "Asia",
    "India": "Asia",
    "Indonesia": "Asia",
    "Japan": "Asia",
    "Kazakhstan": "Asia",
    "Malaysia": "Asia",
    "Nepal": "Asia",
    "Pakistan": "Asia",
    "Philippines": "Asia",
    "Singapore": "Asia",
    "South Korea": "Asia",
    "Sri Lanka": "Asia",
    "Taiwan": "Asia",
    "Thailand": "Asia",
    "Uzbekistan": "Asia",
    "Vietnam": "Asia",

    # Middle East
    "Bahrain": "Middle East",
    "Iran": "Middle East",
    "Israel": "Middle East",
    "Jordan": "Middle East",
    "Kuwait": "Middle East",
    "Lebanon": "Middle East",
    "Oman": "Middle East",
    "Qatar": "Middle East",
    "Saudi Arabia": "Middle East",
    "Turkey": "Middle East",
    "United Arab Emirates": "Middle East",

    # Africa
    "Egypt": "Africa",
    "Kenya": "Africa",
    "Morocco": "Africa",
    "Namibia": "Africa",
    "Nigeria": "Africa",
    "South Africa": "Africa",
    "Tunisia": "Africa",

    # Oceania
    "Australia": "Oceania",
    "New Zealand": "Oceania",
}


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    df["region"] = df["country"].map(COUNTRY_TO_REGION)

    missing_regions = sorted(df.loc[df["region"].isna(), "country"].dropna().unique())

    if missing_regions:
        raise ValueError(f"Missing region mappings for countries: {missing_regions}")

    # Put region after country for readability.
    columns = list(df.columns)
    columns.remove("region")
    country_index = columns.index("country")
    columns.insert(country_index + 1, "region")

    df = df[columns]

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved dataset with region column to: {OUTPUT_PATH}")
    print(df["region"].value_counts())


if __name__ == "__main__":
    main()