# Repository Overview

Last updated: 2026-05-15

## Purpose

This repository supports a live Econ + AI workshop. It is designed to keep the
presentation and live-coded demo close together so the workshop can move from
slides to code with minimal setup.

The primary workflow is:

1. Present the workshop deck in `docs/references/presentation/econ_ai_workshop.pdf`.
2. Live-code or adapt the Streamlit demo from `app/app.py`.
3. Use small local examples, templates, and helper scripts only when they make
   the demo easier to explain.

The repository favors clarity over production architecture. Code should stay
small, readable, and easy to narrate during the talk.

## Top-Level Structure

| Path | Role |
| --- | --- |
| `README.md` | Quick-start summary for the workshop repository. |
| `AGENTS.md` | Instructions for coding agents working in this repo. |
| `app/` | Streamlit demo application and supporting demo assets. |
| `docs/` | Workshop documentation and reference materials. |

## Application Structure

The Streamlit application lives under `app/`.

| Path | Role |
| --- | --- |
| `app/app.py` | Main Streamlit entry point. It configures the page and registers pages. |
| `app/pages/` | Optional Streamlit pages for the demo flow. |
| `app/data/` | Local demo data. Treat contents as potentially sensitive unless confirmed otherwise. |
| `app/src/` | Reusable helper code, templates, scripts, and demo content. |
| `app/src/templates/` | Small reference templates for chat, MCP, and transcription demos. |
| `app/src/scripts/` | Helper scripts grouped by topic, such as `chat/`, `db/`, `plot/`, and `mcp/`. |
| `app/docs/` | App-specific notes, especially template documentation. |
| `app/requirements.txt` | Minimal Python dependencies for the demo app. |

Keep `app/app.py` readable enough to discuss live. Move helper functions into
`app/src/` only when the app becomes too large to explain comfortably in one
place.

## Running The Demo

From the repository root:

```bash
cd app
streamlit run app.py
```

The current app uses Streamlit's native navigation with pages in `app/pages/`.
The dependency set is intentionally minimal.

## Documentation Structure

The `docs/` folder contains workshop-facing material:

| Path | Role |
| --- | --- |
| `docs/repository-overview.md` | High-level map of the repository. |
| `docs/references/` | Reference material used to prepare or deliver the workshop. |
| `docs/references/presentation/` | Presentation source and exported deck. |
| `docs/references/installation_guide/` | Setup guide and related images. |
| `docs/references/slides/` | Additional reference slide decks. |

Use `docs/` for repository-level documentation. Use `app/docs/` for notes that
only matter when working inside the Streamlit app.

## Demo Development Guidelines

- Prefer native Streamlit widgets, layouts, charts, and navigation before adding
  custom components.
- Keep new dependencies rare and easy to justify during the workshop.
- Store local demo data in `app/data/`.
- Put helper scripts under `app/src/scripts/` and group them by purpose.
- Keep reusable code in `app/src/` only when it improves readability.
- Avoid broad refactors that distract from the live-coding story.
- Use simple functions and straightforward control flow.

## Data And Secrets Handling

- Do not commit secrets.
- Do not open, print, or inspect `secrets.toml`.
- Treat files in `app/data/` and other raw data folders as potentially
  sensitive unless the owner confirms they are safe to display.
- When data inspection is needed, report safe derived information such as file
  names, schemas, row counts, data types, validation results, or aggregate
  summaries.

## Common Extension Points

Use these paths when the demo grows:

| Need | Recommended Path |
| --- | --- |
| Add a simple app screen | `app/pages/` |
| Add a small helper function | `app/src/` |
| Add a data download or ingestion script | `app/src/scripts/db/` |
| Add a chat or prompt experiment | `app/src/scripts/chat/` |
| Add a plotting script | `app/src/scripts/plot/` |
| Add an MCP experiment | `app/src/scripts/mcp/` |
| Add app-specific notes | `app/docs/` |
| Add repository-level notes | `docs/` |

## Lightweight Verification Checklist

For small changes:

```bash
python -m py_compile app/app.py
```

For behavior changes:

```bash
cd app
streamlit run app.py
```

Before presenting, confirm:

- The deck exists at `docs/references/presentation/econ_ai_workshop.pdf`.
- The Streamlit app starts without errors.
- Any data needed for the demo is present locally.
- Any optional page or template used in the talk is simple enough to explain.
