# fcsim

Open nuclear fuel cycle scenario simulator (Python + Streamlit).

> Design model. Results reported in the paper were obtained with the IAEA NFCSS code.

Work in progress (milestone M0: skeleton). See `CLAUDE.md` for the full
specification and `docs/assumptions.md` for modelling decisions.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
streamlit run app/Home.py
```

Scenarios are YAML files (see `data/scenarios/`). Values still missing are marked
`PLACEHOLDER` and listed by the app; they are never filled in from memory.
