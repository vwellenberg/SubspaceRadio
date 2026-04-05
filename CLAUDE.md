# SubspaceRadio

Fork von [swingmx/swingmusic](https://github.com/swingmx/swingmusic) — ein selbst-gehosteter Musikplayer/Streaming-Server (Flask + SQLAlchemy Backend, separater Vue.js Webclient).

## Projekt-Setup

- **Repo:** https://github.com/vwellenberg/SubspaceRadio
- **Python:** >=3.11
- **Package Manager:** uv (nicht pip!)
- **Server:** 192.168.0.4, Port 1970, systemd Service `subspaceradio`
- **SSH:** `ssh vwellenberg@192.168.0.4` (ed25519 Key)
- **Webclient:** https://github.com/vwellenberg/SubspaceRadio-Client (Vue.js, yarn, vite)
- **Webclient lokal:** /tmp/SubspaceRadio-Client
- **Webclient auf Server:** ~/SubspaceRadio-Client, deployed nach ~/.config/swingmusic/client/

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
- Tests mit schweren Dependencies nutzen `sys.modules` Mocking (siehe `test_album_model.py`, `test_sortlib.py`)

## Server-Deployment

```bash
# Auf dem Server (192.168.0.4):
cd ~/SubspaceRadio
git pull
sudo -n systemctl restart subspaceradio

# Status (kein sudo nötig):
systemctl status subspaceradio
journalctl -u subspaceradio -f

# Memory beobachten:
ps aux | grep swingmusic | grep -v grep | awk '{print $6/1024"MB"}'
```

Passwordless sudo ist konfiguriert für `systemctl restart/stop/start subspaceradio`.

### Webclient deployen

```bash
cd ~/SubspaceRadio-Client
git pull
NODE_OPTIONS='--dns-result-order=ipv4first' yarn install --network-timeout 120000
NODE_OPTIONS='--dns-result-order=ipv4first' yarn build
rm -rf ~/.config/swingmusic/client
cp -r dist ~/.config/swingmusic/client
sudo -n systemctl restart subspaceradio
```

**Wichtig:** Server hat IPv6-Problem — yarn/npm brauchen `NODE_OPTIONS='--dns-result-order=ipv4first'`.

## Was bisher gemacht wurde

- Ruff Linting + Formatting (483 → 0 Issues)
- Pre-commit Hooks (ruff + mypy)
- CI Pipeline (GitHub Actions: Lint, Format, Mypy, Tests)
- 86 pytest Tests (Hashing, Parsers, Dates, Utils, Album-Model, Folder-Sorting)
- mypy strict für 4 Utils-Module
- Alphabetische Sortierung als Default für Ordner und Playlists
- Memory Leak Fixes (PIL Images, Watchdog, TransCodeStore, mutable default arg)

## Nächste Schritte

Siehe [ROADMAP.md](ROADMAP.md). Frontend-Änderungen (Ordner-Listenansicht, Playlist Drag & Drop, Auto-Tag Button) können jetzt im Webclient-Fork gemacht werden.
