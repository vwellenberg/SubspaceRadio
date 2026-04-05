# SubspaceRadio

Fork von [swingmx/swingmusic](https://github.com/swingmx/swingmusic) — ein selbst-gehosteter Musikplayer/Streaming-Server (Flask + SQLAlchemy Backend, separater Vue.js Webclient).

## Projekt-Setup

- **Repo:** https://github.com/vwellenberg/SubspaceRadio
- **Python:** >=3.11
- **Package Manager:** uv (nicht pip!)
- **Server:** 192.168.0.4, Port 1970, systemd Service `subspaceradio`
- **Webclient:** Separates Repo `swingmx/webclient` (noch nicht geforkt)

## Entwicklung

```bash
# Dependencies installieren
uv sync

# Linting
uvx ruff check src/ tests/
uvx ruff format src/ tests/

# Tests (brauchen extra deps wegen bjoern build-Problem lokal)
uvx --with xxhash --with unidecode --with pendulum --with requests pytest tests/ -v --ignore=tests/test_split_artists.py

# Type checking (nur strikte Module)
uvx --with xxhash --with unidecode --with pendulum mypy src/swingmusic/utils/hashing.py src/swingmusic/utils/dates.py src/swingmusic/utils/parsers.py src/swingmusic/utils/__init__.py --config-file pyproject.toml
```

## Code-Qualität

- **Ruff:** Linting + Formatting, konfiguriert in `pyproject.toml`
- **mypy:** Graduelle Einführung — aktuell strict für `utils/hashing.py`, `utils/dates.py`, `utils/parsers.py`, `utils/__init__.py`. Neue Module bei Bearbeitung zur strict-Liste hinzufügen.
- **Pre-commit Hooks:** ruff check --fix, ruff format, mypy (strikte Module)
- **CI:** GitHub Actions bei jedem Push/PR — Lint, Format, Mypy, Tests
- **Vendored Code:** `src/swingmusic/lib/pydub/` ist Third-Party, von Linting/Mypy ausgeschlossen

## Architektur-Hinweise

- `src/swingmusic/lib/pydub/` — vendored pydub, nicht anfassen
- `tests/test_split_artists.py` — alter unittest-Test, wird in CI ignoriert (dupliziert durch test_parsers.py)
- `bjoern` (WSGI-Server) braucht `libev-dev` + `python3-dev` zum Bauen — fehlt in vielen Umgebungen, daher CI-Tests mit `uvx` statt `uv run`

## Server-Deployment

```bash
# Auf dem Server (192.168.0.4):
cd ~/SubspaceRadio
git pull
sudo systemctl restart subspaceradio
```

## Nächste Schritte

Siehe [ROADMAP.md](ROADMAP.md) — Playlist- und Ordner-Verbesserungen + Memory Leak Analyse. Frontend-Änderungen erfordern einen Fork des Webclient-Repos.
