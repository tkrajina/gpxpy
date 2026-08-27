# AGENTS.md — gpxpy

## Developer Commands

- Run all tests: `make test` or `python3 -m unittest test`
- Run single test: `python3 -m unittest test.GPXTests.test_method_name`
- Run mypy (strict): `make mypy` → `mypy --strict . gpxinfo`
- Full verification: `make mypy-and-tests` (runs mypy → gpxinfo → tests)
- Build for PyPI: `make pypi-upload`

## Branch Workflow

- `master` = latest release code
- `dev` = next release (send PRs here, not to `master`)
- CI runs on `main` and `dev` branches

## Architecture

- Single package library: `gpxpy/` (not a monorepo)
- Entry point: `gpxpy/__init__.py` exposes `parse()` and `__version__`
- Core modules:
  - `gpx.py` — GPX data model (GPX, GPXTrack, GPXTrackSegment, GPXTrackPoint, etc.)
  - `parser.py` — XML parsing (GPXParser class)
  - `gpxfield.py` — field definitions and timezone handling
  - `gpxxml.py` — XML serialization
  - `geo.py` — geographic calculations (distance, haversine, course)
  - `utils.py` — helpers
- `py.typed` marker present → PEP 561 compliant (type checkers use inline types)
- `gpxinfo` — standalone CLI script in repo root (must also pass mypy)

## Testing

- All tests in single file: `test.py` (class `GPXTests`)
- Test fixtures in `test_files/` directory
- No pytest — uses stdlib `unittest`
- lxml is optional; tests auto-detect and skip lxml-specific tests if unavailable

## Type Checking

- mypy runs with `--strict` flag
- Both `.gpxpy` and `gpxinfo` script must pass
- Type hints required on all new code

## Toolchain Quirks

- XML parser: lxml preferred (2-3x faster), falls back to xml.etree.ElementTree
- GPX versions: supports 1.0 and 1.1; version auto-detected or forced via `parse(..., version="1.0")`
- No `pyproject.toml` — uses legacy `setup.py`
- No pre-commit hooks, no tox, no linting configured beyond mypy

## Python Support

- Minimum Python 3.6 (enforced in setup.py)
- CI tests against Python 3.8–3.15
