# Agent Instructions

## Purpose

This repository exists for a live Econ + AI workshop presentation. The main flow is:

- Give the talk using `docs/references/presentation/econ_ai_workshop.pdf`.
- Live-code a simple demo app from `app/app.py`.

Optimize for a smooth live demo, not for production architecture.

## Working Style

- Prefer efficient, direct changes that can be explained during a talk.
- Keep the tech stack simple: Python, Streamlit, and small local files unless the user asks for more.
- Use existing templates, examples, or local patterns whenever they are close enough.
- Avoid adding infrastructure, frameworks, services, or complex abstractions unless they clearly help the demo.
- Keep dependencies minimal and add a new package only when it meaningfully improves the live-coding result.
- Favor readable code over clever code. The audience should be able to follow the implementation in real time.
- Keep Python code as simple as possible: prefer plain functions, straightforward control flow, and standard-library tools before introducing classes, advanced patterns, or extra helpers.

## App Guidance

- Treat `app/app.py` as the Streamlit entry point.
- Keep demo data in `app/data/` when local data is needed.
- Put reusable helper functions in `app/src/` only after the app becomes too large to read comfortably.
- Use `app/pages/` only if a multi-page Streamlit demo is explicitly useful.
- Prefer native Streamlit widgets and charts before custom HTML, JavaScript, or components.
- Never open, read, print, diff, parse, edit, or write any `secrets.toml` file. If secrets are needed, ask the user to manage the file directly and only discuss required key names or redacted examples outside of `secrets.toml`.

## Script Organization

- Keep helper scripts under `app/src/scripts/` and split them by purpose instead of putting scripts directly in the root of that folder.
- Use `app/src/scripts/chat/` for chat prompts, chat API experiments, and conversation utilities.
- Use `app/src/scripts/db/` for data download, database setup, query, and ingestion utilities.
- Use `app/src/scripts/plot/` for chart generation, figure export, and plotting experiments.
- Use `app/src/scripts/mcp/` for MCP server/client experiments and connector utilities.
- If a new script does not fit those folders, create a small, clearly named subfolder for its topic.

## Data Handling

- Do not expose, paste, print, screenshot, or manually open proprietary or potentially sensitive data files.
- Do not inspect data files with tools such as `cat`, `sed`, `head`, `tail`, `less`, or text search when the contents may be proprietary.
- When data processing is needed, use Python code to load and transform the data programmatically, and only report safe derived information such as file names, schema, row counts, column names, data types, validation results, or aggregate summaries.
- Avoid showing raw rows or raw cell values unless the user explicitly confirms the data is safe to display.
- Keep proprietary data out of commits and generated outputs unless the user explicitly asks otherwise.

## Verification

- For small edits, run a fast syntax check such as `python -m py_compile app/app.py`.
- For app behavior changes, prefer `streamlit run app/app.py` and verify the page loads.
- Do not spend time on broad test suites unless the user asks for them or the change adds real logic.
