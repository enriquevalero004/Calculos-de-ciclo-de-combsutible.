import pytest
from pydantic import ValidationError

from fcsim.models import (
    PLACEHOLDER,
    DeploymentPath,
    Fleet,
    Fuel,
    ReactorType,
    Scenario,
    Segment,
)

REACTOR = dict(
    name="R",
    spectrum="thermal",
    fuel="UOX",
    unit_power_mwe=1000.0,
    thermal_efficiency=0.33,
    load_factor=0.9,
    discharge_burnup_gwd_per_thm=50.0,
    n_batches=3,
    initial_core_factor=1.0,
    cooling_time_y=5.0,
    leakage_reactivity=0.0,
)


def test_custom_fuel_composition_must_sum_to_one():
    Fuel(name="c", kind="CUSTOM", composition={"U-235": 0.05, "U-238": 0.95})
    with pytest.raises(ValidationError, match="sum to"):
        Fuel(name="c", kind="CUSTOM", composition={"U-235": 0.05, "U-238": 0.9})


def test_composition_tolerance_is_1e_6():
    Fuel(name="c", kind="CUSTOM", composition={"U-235": 0.05, "U-238": 0.95 + 5e-7})
    with pytest.raises(ValidationError):
        Fuel(name="c", kind="CUSTOM", composition={"U-235": 0.05, "U-238": 0.95 + 2e-6})


def test_bad_nuclide_name_rejected():
    with pytest.raises(ValidationError, match="invalid nuclide"):
        Fuel(name="c", kind="CUSTOM", composition={"U235": 1.0})


def test_fuel_kind_required_fields():
    with pytest.raises(ValidationError, match="enrichment_wt"):
        Fuel(name="u", kind="UOX")
    with pytest.raises(ValidationError, match="pu_content_wt"):
        Fuel(name="m", kind="MOX", pu_vector_source="stock", u_matrix="depleted")
    with pytest.raises(ValidationError, match="pu_vector"):
        Fuel(name="m", kind="MOX", pu_content_wt=10, pu_vector_source="fixed", u_matrix="depleted")
    with pytest.raises(ValidationError, match="only contain Pu"):
        Fuel(
            name="m", kind="MOX", pu_content_wt=10, pu_vector_source="fixed",
            u_matrix="depleted", pu_vector={"U-238": 1.0},
        )


def test_weight_percent_range():
    with pytest.raises(ValidationError):
        Fuel(name="u", kind="UOX", enrichment_wt=120)


def test_placeholder_accepted_but_other_strings_not():
    ReactorType(**{**REACTOR, "load_factor": PLACEHOLDER})
    with pytest.raises(ValidationError):
        ReactorType(**{**REACTOR, "load_factor": "unknown"})


def test_reactor_needs_exactly_one_of_batches_and_residence():
    with pytest.raises(ValidationError, match="exactly one"):
        ReactorType(**{**REACTOR, "residence_time_y": 4.0})
    no_batches = {k: v for k, v in REACTOR.items() if k != "n_batches"}
    with pytest.raises(ValidationError, match="exactly one"):
        ReactorType(**no_batches)
    ReactorType(**no_batches, residence_time_y=4.0)


def test_unknown_fields_rejected():
    with pytest.raises(ValidationError):
        ReactorType(**REACTOR, power_mw=3)


def test_segments_validation():
    with pytest.raises(ValidationError, match="t1_year"):
        Segment(function="constant", t0_year=2050, t1_year=2050, p0_mwe=1.0)
    with pytest.raises(ValidationError, match="needs k"):
        Segment(function="logistic", t0_year=2025, t1_year=2050, p0_mwe=0.0, p1_mwe=1.0)
    with pytest.raises(ValidationError, match="overlap"):
        DeploymentPath(segments=[
            Segment(function="linear", t0_year=2025, t1_year=2050, p0_mwe=0, p1_mwe=10),
            Segment(function="constant", t0_year=2040, t1_year=2060),
        ])
    with pytest.raises(ValidationError, match="continuous"):
        DeploymentPath(segments=[
            Segment(function="linear", t0_year=2025, t1_year=2050, p0_mwe=0, p1_mwe=10),
            Segment(function="linear", t0_year=2050, t1_year=2060, p0_mwe=5, p1_mwe=20),
        ])
    DeploymentPath(segments=[
        Segment(function="linear", t0_year=2025, t1_year=2050, p0_mwe=0, p1_mwe=10),
        Segment(function="linear", t0_year=2050, t1_year=2060, p0_mwe=5, p1_mwe=20, continuous=False),
    ])


def _scenario(**overrides):
    base = dict(
        name="s",
        start_year=2025,
        end_year=2100,
        fuels=[Fuel(name="UOX", kind="UOX", enrichment_wt=4.5)],
        reactor_types=[ReactorType(**REACTOR)],
        fleets=[Fleet(name="F", reactor_type="R")],
    )
    return Scenario(**{**base, **overrides})


def test_scenario_references_are_checked():
    _scenario()
    with pytest.raises(ValidationError, match="unknown reactor type"):
        _scenario(fleets=[Fleet(name="F", reactor_type="X")])
    with pytest.raises(ValidationError, match="unknown fuel"):
        _scenario(reactor_types=[ReactorType(**{**REACTOR, "fuel": "MOX"})])
    with pytest.raises(ValidationError, match="unknown fleet"):
        _scenario(fleets=[Fleet(name="F", reactor_type="R", replaces="G")])
    with pytest.raises(ValidationError, match="itself"):
        _scenario(fleets=[Fleet(name="F", reactor_type="R", replaces="F")])
    with pytest.raises(ValidationError, match="duplicate"):
        _scenario(fleets=[Fleet(name="F", reactor_type="R"), Fleet(name="F", reactor_type="R")])
    with pytest.raises(ValidationError, match="unknown fleets"):
        _scenario(cycle={"reprocessed_fraction": {"G": 1.0}})


def test_scenario_years():
    with pytest.raises(ValidationError):
        _scenario(end_year=2201)
    with pytest.raises(ValidationError, match="after start_year"):
        _scenario(end_year=2025)


def test_pu_content_only_for_mox():
    with pytest.raises(ValidationError, match="pu_content_wt"):
        _scenario(reactor_types=[ReactorType(**REACTOR, pu_content_wt=17.0)])


def test_initial_pu_needs_vector():
    with pytest.raises(ValidationError, match="pu_vector"):
        _scenario(initial_stocks={"separated_pu_t": 100.0})


def test_placeholders_are_listed():
    scenario = _scenario(reactor_types=[ReactorType(**{**REACTOR, "load_factor": PLACEHOLDER})])
    paths = scenario.placeholders()
    assert "reactor_types.R.load_factor" in paths
    assert "cycle.losses.mining_milling" in paths  # losses default to PLACEHOLDER
