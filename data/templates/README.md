# Templates: sources

Every number in these files must have a source. Values not yet provided are the
literal string `PLACEHOLDER`; the app lists them and warns until they are filled in.

| File | Field | Value | Source |
|---|---|---|---|
| reactors/ap1000.yaml | unit_power_mwe | 1117 MWe | Actual AP1000 net power, as fixed in CLAUDE.md §1 (the TFG phases I–V used 1000 MWe) |
| reactors/ap1000.yaml | enrichment_wt / discharge_burnup_gwd_per_thm | 4.5 wt% / 60 GWd/tHM | TFG reference pair, CLAUDE.md §4.3 |
| reactors/esfr_smart.yaml | pu_content_wt / discharge_burnup_gwd_per_thm | 17.99 wt% / 100 GWd/tHM | TFG reference pair, CLAUDE.md §4.3 |
| reactors/esfr_smart.yaml | initial_core_factor | 0.63 | NFCSS value quoted as "≈ 0.63" in CLAUDE.md §1; exact value to confirm |
| fuels/uox.yaml | enrichment_wt | 4.5 wt% | Same as AP1000 |
| fuels/mox.yaml | pu_content_wt | 17.99 wt% | Same as ESFR-SMART |

Pending (PLACEHOLDER), to be taken from TFG Table 5-4: thermal efficiency, load
factor, number of batches or residence time, initial core factor (AP1000), tails
assay, cooling time, ESFR-SMART unit power. `leakage_reactivity` is calibrated in M2.
