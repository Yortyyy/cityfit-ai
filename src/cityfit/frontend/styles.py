from cityfit.frontend.styles.loader import load_css


def render_globe_styles() -> None:
    load_css(
        "base.css",
        "sidebar.css",
        "methodology.css",
        "search.css",
        "hero.css",
        "city_profile.css",
        "metric_table.css",
        "comparison.css",
        "similar_cities.css",
    )