# Port Houston — Container Service Network

An interactive world map of the 19 container liner services calling Port Houston, drawn along their real
sea-lane routes. Built for ONE Architecture & Urbanism from the Port Houston Container Service Schedule
(revised January 2026).

**Live map:** _(GitHub Pages URL appears here once Pages is enabled)_

## What it shows
Each service is drawn as a line coloured by trade lane, following the navigable shipping lane between its
published ports of call (through the Panama and Suez canals, Gibraltar, and Malacca). The base is a
continuous globe (CARTO Positron via MapLibre GL). Filter by lane, hover or tap a route for its full
rotation, and pin individual services to compare them.

These are sea-lane routes, not live AIS vessel tracks. Where a line meets land it is following a canal or
a river to an inland port (Manaus on the Amazon, New Orleans on the Mississippi). See
[METHODOLOGY.md](METHODOLOGY.md) and [source.md](source.md).

## Repository layout
```
docs/                 the published web map (GitHub Pages serves this folder)
  index.html          MapLibre app
  data/*.geojson      routes + ports
data/                 curated source tables + basemap inputs
  ports.json          canonical port table (coords, routing basin, interpretation flags)
  services.json       the 19 services: cleaned rotation + verbatim PDF text + notes
  searoutes.json      precomputed sea-lane geometry per leg
build/                reproducible build scripts (Python standard library, except searoute)
  precompute_routes.py  generate searoutes.json (needs: pip install searoute)
  build_web.py          emit docs/data/*.geojson
  build.py + template.html  the earlier self-contained static map
  export_gis.py         export ArcGIS shapefiles + GeoJSON
gis_export/           ArcGIS-ready shapefiles (routes by service / by leg, ports)
source.md             provenance
METHODOLOGY.md        methodology contract, assumptions, validation
```

## View locally
```bash
python -m http.server 8788 --directory docs
```
Then open http://localhost:8788/ (the map fetches its GeoJSON, so it needs http, not file://).

## Rebuild the data
```bash
pip install searoute
python build/precompute_routes.py   # data/searoutes.json
python build/build_web.py           # docs/data/*.geojson
python build/export_gis.py          # gis_export/ shapefiles
```

## Credits
Data: Port Houston. Routing: searoute marine network. Basemap: CARTO Positron / OpenStreetMap.
Type: Barlow (a free stand-in for the ONE site's licensed Zed Display).
