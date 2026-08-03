# Source & Provenance

## Primary source
- **Dataset:** Port Houston Container Service Schedule
- **Revision:** "Revised January 2026" (printed on the sheet)
- **File:** `2026-Container-Service-Schedule.pdf` (1 page, 19 services)
- **URL:** https://porthouston.com/wp-content/uploads/2026/02/2026-Container-Service-Schedule.pdf
- **Retrieved:** 2026-07-31
- **Publisher:** Port Houston (Port of Houston Authority)
- **Currency check (2026-07-31):** A web search found no annual revision newer than January 2026. This is the current published planning schedule. Live, per-vessel movements are published separately as daily terminal schedules:
  - Bayport (BPT): https://info.porthouston.com/vtraffic/BAY/BPT%20Vessel%20Schedule.pdf
  - Barbours Cut (BCT): https://info.porthouston.com/vtraffic/bct/BCT%20Vessel%20Schedule.pdf

## What the source contains, and what it does not
The schedule gives, per service: trade lane, service name/ID, average vessel size (TEU), an ordered **port-call rotation**, and the Houston terminal (BPT = Bayport, BCT = Barbours Cut). It does **not** contain vessel tracks, sailing dates, or frequencies. The rotation is a sequence of port names only.

## Derived / staged data
- `data/ports.json` — hand-curated canonical port table (name, approximate WGS84 lat/lon, routing basin, interpretation flags). Coordinates are approximate port locations, adequate for a world-scale schematic; they are not survey-grade berth positions.
- `data/services.json` — the 19 services with cleaned `rotation` (keys into ports.json), the verbatim `raw` PDF text, and `notes` recording every cleanup decision.
- `data/searoutes.json` — sea-lane geometry per leg, generated with the `searoute` Python library (v1.6.0, global marine network; `append_orig_dest=True`). Longitudes normalized to [-180,180].
- `data/ne_110m_land.geojson` — Natural Earth 1:110m land, public domain (basemap, inlined in the map).
- `data/ne_50m_land.geojson` — Natural Earth 1:50m land, public domain (used only to verify routes against a finer coastline; not shipped in the map).

## Processing applied before staging
1. Text extracted from the PDF and each rotation normalized by hand (OCR-style artifacts, duplicated legs, terminal codes, and ambiguous names resolved — all logged in `services.json` notes and `ports.json` flags).
2. Sea-lane geometry computed per leg with `searoute` (`build/precompute_routes.py`).
3. Map assembled from the curated data with `build/build.py` (Python standard library only) into the self-contained `houston_container_routes.html`.

## License / use
Schedule content is Port Houston's. Natural Earth and the searoute network data are open. This map is an internal analytical product for ONE Architecture & Urbanism.

## Reproduce
```bash
python build/precompute_routes.py   # regenerate data/searoutes.json (needs: pip install searoute)
python build/build.py               # assemble houston_container_routes.html
```
