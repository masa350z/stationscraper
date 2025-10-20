# Repository Guidelines

## Project Philosophy: Personal Development Focus

This is a **hobby/learning project**, not enterprise software. Priority is **simplicity and clarity** over scalability or robustness.

### Development Principles
- **YAGNI (You Aren't Gonna Need It)**: Don't build features until actually needed
- **KISS (Keep It Simple)**: Choose obvious solutions over clever ones
- **Responsibility Separation**: Each file/function should have one clear purpose
- **Self-Documenting Code**: Clear naming over extensive comments
- **Remove Dead Code**: Delete unused files, functions immediately

### What to AVOID (unless specifically required)
- Complex error handling or comprehensive logging
- Advanced design patterns or architectural abstractions  
- Performance optimizations before performance problems exist
- Sophisticated security or validation beyond basic needs
- Enterprise frameworks when simple libraries suffice

### Code Quality Focus Areas
1. **Clear module boundaries**: `scrapers/` only scrape, `apis/` only call APIs, `pipeline/` only process data
2. **Simple data flow**: Avoid complex state, prefer pure functions where possible
3. **Readable variable/function names**: `get_station_prices()` not `gsp()`
4. **Minimal dependencies**: Use standard library first, add packages only when necessary
5. **No orphaned code**: Remove empty files like `src/apis/analysis.py` immediately

## Project Structure & Module Organization
- `src/`: Data pipeline (entry `make_base_data.py`), scrapers (`scrapers/`), APIs (`apis/`), processing (`pipeline/`), config (`config.py`).
- `data/`: Inputs and generated CSVs (e.g., `output/price_info`, `output/route_info`, `output/merged`).
- `mapapp/`: Dockerized web app (Flask + Leaflet) for visualization.
- `.env`: API keys. Never commit this file.

## Build, Test, and Development Commands
- Setup: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt` (ensure `python-dotenv` is installed).
- Run pipeline: `cd src && python make_base_data.py` (generates CSVs under `data/output/`).
- Run web app: `cd mapapp && docker-compose up` (opens http://localhost:5000).
- Quick checks: confirm files like `data/output/merged/merged_with_coordinates.csv` are produced.

## Coding Style & Naming Conventions
- **Python, PEP 8**: 4‑space indent, `snake_case` for files/functions/variables
- **Module focus**: Each file should have one clear responsibility
- **Function design**: Prefer pure functions (input → output) over stateful operations
- **Naming clarity**: `scrape_station_prices()` not `scrape_data()`, `merge_station_info()` not `merge()`
- **Comments/docstrings**: Japanese to match existing codebase
- **I/O boundaries**: Keep external calls (`requests`, file operations) in `scrapers/` and `apis/`, pure data transformation in `pipeline/`
- **No magic numbers**: Use constants in `config.py` instead of hardcoded values

## Testing Guidelines
- No formal test suite yet. Use smoke runs and CSV diffs.
- Validate row counts and key columns after each stage (e.g., merged keys `['line','station']`).
- If adding tests, use `pytest`, place under `tests/`, name `test_*.py`; no coverage gate yet.

## Commit & Pull Request Guidelines
- Commits: short present‑tense summaries; JP/EN both fine. Example: `scraper: SUUMO 家賃相場の空値除外`.
- PRs include: purpose, scope, run steps, data impact (new/changed CSVs), and screenshots/logs when UI changes.
- Link related issues; avoid committing large data or secrets.

## Security & Configuration Tips
- Required env vars in `.env`: `EKISPERT_KEY`, `GOOGLE_MAPS_KEY`.
- Be polite to targets: tune `SCRAPING_SLEEP_SEC` and `SCRAPING_RETRY_COUNT` in `src/config.py`.
- Update `WALK_MINUTES` and `ROOM_TYPE` in `config.py` for new targets; keep defaults sensible.
