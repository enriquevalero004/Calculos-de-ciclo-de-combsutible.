"""UI strings. English is the default; add a "es" dictionary to translate."""

from __future__ import annotations

LANGUAGE = "en"

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "app_title": "fcsim — open nuclear fuel cycle simulator",
        "disclaimer": "Design model. Results reported in the paper were obtained with the IAEA NFCSS code.",
        "home_intro": (
            "Define a reactor fleet, its fuels and deployment paths, and compute the material "
            "flows of an open or closed nuclear fuel cycle."
        ),
        "scenario_section": "Scenario",
        "load_demo": "Load a bundled scenario",
        "upload_yaml": "Or upload a scenario YAML",
        "load": "Load",
        "loaded": "Loaded scenario: {name} ({start}–{end})",
        "no_scenario": "No scenario loaded. Load one from the Home page.",
        "invalid_yaml": "Invalid scenario file: {error}",
        "placeholders_warning": (
            "{n} input values are still PLACEHOLDER (missing data, never filled in from memory). "
            "Results that depend on them cannot be computed yet."
        ),
        "placeholders_list": "Show PLACEHOLDER fields",
        "coming_soon": "This page is implemented in milestone {milestone}.",
        "page_fuels": "Fuels",
        "page_reactors": "Reactors",
        "page_fleet": "Fleet and deployment",
        "page_cycle": "Fuel cycle",
        "page_results": "Results",
        "page_diagnostics": "Closed cycle diagnostics",
        "page_validation": "Validation",
        "page_export": "Export",
        "download_yaml": "Download scenario YAML",
    },
}


def t(key: str, **kwargs: object) -> str:
    """Translated string for ``key``, falling back to English."""
    text = STRINGS.get(LANGUAGE, {}).get(key) or STRINGS["en"][key]
    return text.format(**kwargs) if kwargs else text
