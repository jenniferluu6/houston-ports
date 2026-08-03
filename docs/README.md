# Port Houston Container Network — web map

Self-hosted interactive map (MapLibre GL JS + CARTO Positron basemap). Not self-contained: it loads
the map library, basemap tiles, and fonts from the network at view time, so it needs internet access
but no build server.

## Contents
```
index.html            the app
data/routes.geojson   one polyline per service (colored by trade lane)
data/ports.geojson    port points
```

## View it locally
```bash
cd path/to/houston_ports
python -m http.server 8788 --directory web
```
Then open http://localhost:8788/ . (Opening index.html directly with file:// will not work — the
GeoJSON is fetched, which needs http.)

## Deploy (pick one)
- **Cloudflare Pages** (recommended for ONE): create a project, upload this `web/` folder as the build
  output (or connect a repo with `web/` as the root). No build command needed.
- **GitHub Pages**: put the contents of `web/` at the repo root (or `/docs`), enable Pages.
- Any static host (Netlify, S3 + CloudFront, etc.) works — it's plain static files.

## External dependencies (loaded at runtime)
- MapLibre GL JS 4.7.1 — unpkg CDN
- CARTO Positron basemap style + tiles — basemaps.cartocdn.com (attribution shown on map; confirm
  CARTO's current basemap terms for production use)
- Barlow / Barlow Semi Condensed — Google Fonts

## Fonts
This build uses **Barlow** (body) and **Barlow Semi Condensed** (display) as free stand-ins for the ONE
site's licensed **Zed Display** faces. To match the site exactly, drop the Zed woff2 files into
`web/fonts/`, add matching `@font-face` rules, and swap the `--disp` / `--sans` CSS variables in
`index.html`.

## Regenerate the data
The GeoJSON is produced from the curated source tables:
```bash
python build/build_web.py
```
Routes are real sea-lane geometry (searoute), split at the antimeridian into multipart lines.
