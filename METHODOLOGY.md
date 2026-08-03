# Methodology — Port Houston container-route map (schematic v1)

## What this map is
A static, interactive world map of the 19 container liner services that call Port Houston, drawn along real sea-lane routes between each service's published ports of call. It answers "where do the boxes go from Houston, and by roughly what corridor." It is a schematic planning view, not a live operations tool.

## What this map is not
The lines are **sea-lane routes**, computed on a marine network, not recorded vessel tracks. A real "actual path the boats take" needs AIS position data (a paid, live feed and a separate pipeline). The schedule this is built from is a January 2026 planning document; individual services get reshuffled through the year, so treat service membership as of early 2026.

## Data manifest
See `source.md`. In short: one source PDF (rev. Jan 2026), a hand-curated port table, cleaned rotations with the raw text preserved, searoute-generated leg geometry, and a Natural Earth basemap.

## Processing chain
1. **Extract** the 19 rotations from the PDF.
2. **Normalize** each rotation by hand. Every decision is logged (`services.json` notes, `ports.json` flags). Two classes of token are dropped from the drawn route and flagged:
   - `AAOPT` — a Port Houston terminal/berth code that appears mid-rotation in several services, not a foreign port.
   - `Escobedo` (VICTORY) — no known seaport; General Escobedo is inland Nuevo Leon.
3. **Geocode** each unique port to an approximate location and assign a routing basin.
4. **Route** each consecutive leg with `searoute` (marine network; passes through canals and shipping lanes). Longitudes are normalized to [-180,180].
5. **Assemble** the self-contained HTML with the Robinson projection, splitting every polyline at the antimeridian so Pacific crossings render correctly.

## Key assumptions & interpretations
- Ambiguous port names were read from context and flagged in `ports.json`. The load-bearing ones: bare "Freeport" = Freeport, Grand Bahama (not Freeport TX); "Manzanillo" = Manzanillo/Colon, Panama (not the Mexican Pacific port); "San Salvador" = San Salvador Island, Bahamas (and dropped as a doubled-text artifact); "Trivandrum" = Vizhinjam; "Jawaharlal Nehru" = Nhava Sheva. "Conde" (Brazil) is low-confidence.
- "Panama City" is read two ways by service: **LONESTAR** = Panama (Pacific), which sits next to Rodman/Balboa in that rotation; **LPU** (a 200-TEU Houston-Progreso Gulf feeder) = Panama City, FL, since a feeder that size transiting the canal to Pacific Panama is implausible. LPU's reading is the single call most worth verifying with the carrier.
- MSC MEDGULF calls **Barcelona twice per cycle** (after Las Palmas, and again after Genoa); both are drawn.
- MSC MEDGULF prints its loop twice; it was collapsed to a single cycle re-anchored at Houston.
- FAR EAST PEX3 reads as a near round-the-world listing; its printed order may not be one physical loop.
- The ring-based chokepoint router in `ports.json` (gateways / edge_gateways) was an earlier approach. The shipped map uses `searoutes.json` geometry directly, so that router is not on the critical path.

## Uncertainty
- Port coordinates are approximate (world-scale schematic; not berth-accurate).
- Sea-lane routes are network shortest-paths, not the exact lane a given carrier sails, and not AIS.
- Amazon (Manaus, Itacoatiara), Mississippi (New Orleans), and canal (Panama, Suez) segments trace waterways that a coarse basemap renders as land. They are correct navigation, not errors.

## Validation gate (what was checked)
- **Currency:** confirmed Jan 2026 is the latest published annual schedule (2026-07-31).
- **Land crossings:** every leg's geometry was tested against Natural Earth 1:50m land (buffered 0.15deg inward), after splitting at the antimeridian. The only >40 km "overland" segments are the Amazon river ports, the Mississippi approach to New Orleans, Suez/Panama canal transits, and the one low-confidence port (Conde). No route crosses open land.
- **Interactivity:** lane filtering, route hover tooltips (full rotation), and light/dark themes verified in a browser served over HTTP.
- **Rotation fidelity & coordinates:** an independent adversarial review diffed all 19 rotations token-by-token against the PDF and spot-checked coordinates. Findings are recorded with the deliverable.

## Regenerate
```bash
python build/precompute_routes.py
python build/build.py
```
