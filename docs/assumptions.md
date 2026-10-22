# Modelling assumptions and conventions

Every physical or modelling decision not fixed in `CLAUDE.md` is recorded here with
its justification and source. Items marked **to confirm** are pending Enrique's review.

## M0 — data model

1. **Units of enrichment and Pu content.** `enrichment_wt`, `pu_content_wt` and
   `tails_assay_wt` are in weight percent of heavy metal (4.5 means 4.5 %), as
   written in the TFG. Isotopic compositions (`composition`, `pu_vector`) are mass
   fractions that sum to 1 (tolerance 1e-6).
2. **Missing data.** Unknown values are stored as the literal `PLACEHOLDER` in the
   YAML; `Scenario.placeholders()` lists them and the app shows a warning. The
   defaults of all losses, delays, the Pu reserve and the HLW glass factor are
   `PLACEHOLDER`, not zero, so that no number is assumed silently.
3. **Cooling time.** Stored per reactor type (`ReactorType.cooling_time_y`), with an
   optional per-fleet override in `cycle.delays.cooling_y`.
4. **Reprocessed fraction.** Given per fleet in `cycle.reprocessed_fraction`;
   fleets that are not listed reprocess nothing.
5. **Residence time vs. batches.** A reactor type gives exactly one of
   `residence_time_y` and `n_batches`; the other is derived in M1/M2.
6. **Manual deployment edits.** Two maps, `manual_delta_mwe` and `manual_set_mwe`,
   applied after the functional segments; the "set" values are applied after the
   deltas of the same year.
7. **MOX template U matrix = depleted U** (**to confirm**).
8. **ESFR-SMART `initial_core_factor` = 0.63**, quoted as approximate in CLAUDE.md
   (**to confirm** exact NFCSS value).
