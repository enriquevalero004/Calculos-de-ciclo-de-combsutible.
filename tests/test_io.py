import pytest

from fcsim.io import (
    data_dir,
    list_templates,
    load_fuel_template,
    load_reactor_template,
    load_scenario,
    scenario_from_yaml,
    scenario_to_yaml,
)


def test_yaml_roundtrip_is_identical(demo_scenario):
    text = scenario_to_yaml(demo_scenario)
    again = scenario_from_yaml(text)
    assert again == demo_scenario
    assert scenario_to_yaml(again) == text


def test_file_roundtrip(tmp_path, demo_scenario):
    from fcsim.io import dump_scenario

    path = tmp_path / "s.yaml"
    dump_scenario(demo_scenario, path)
    assert load_scenario(path) == demo_scenario


@pytest.mark.parametrize("name", list_templates("scenarios"))
def test_bundled_scenarios_load(name):
    load_scenario(data_dir() / "scenarios" / f"{name}.yaml")


def test_templates_load():
    assert set(list_templates("reactors")) == {"ap1000", "esfr_smart"}
    assert set(list_templates("fuels")) == {"uox", "mox"}
    ap1000 = load_reactor_template("ap1000")
    assert ap1000.unit_power_mwe == 1117.0
    assert load_reactor_template("esfr_smart").spectrum.value == "fast"
    assert load_fuel_template("mox").pu_content_wt == 17.99
    assert load_fuel_template("uox").enrichment_wt == 4.5


def test_template_fuel_references_match():
    for reactor in ("ap1000", "esfr_smart"):
        fuel_name = load_reactor_template(reactor).fuel
        assert fuel_name in {load_fuel_template(f).name for f in list_templates("fuels")}
