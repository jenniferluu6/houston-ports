#!/usr/bin/env python3
"""Emit web GeoJSON for the MapLibre map: one polyline per service + port points.
Reads the curated source tables and writes web/data/routes.geojson and web/data/ports.geojson.
Lines are split at the antimeridian into MultiLineString parts. Standard library only."""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
WEB = ROOT / "docs" / "data"; WEB.mkdir(parents=True, exist_ok=True)   # /docs = GitHub Pages site root

ports    = json.load(open(DATA/"ports.json", encoding="utf-8"))["ports"]
services = json.load(open(DATA/"services.json", encoding="utf-8"))["services"]
routes   = json.load(open(DATA/"searoutes.json", encoding="utf-8"))
TERM = {"BPT": "Bayport", "BCT": "Barbours Cut"}

def unwrap(coords):
    """Make longitudes continuous (allowed to run past +/-180) so a route crossing the
    antimeridian is ONE unbroken line. MapLibre + renderWorldCopies wrap it seamlessly;
    no split, so no gap in the middle of the ocean."""
    out = [[coords[0][0], coords[0][1]]]
    for i in range(1, len(coords)):
        lon, prev = coords[i][0], out[-1][0]
        while lon - prev > 180:  lon -= 360
        while lon - prev < -180: lon += 360
        out.append([lon, coords[i][1]])
    return out

def service_coords(rot):
    coords = []
    for i in range(len(rot)-1):
        if rot[i] == rot[i+1]: continue
        leg = routes.get(rot[i]+">"+rot[i+1])
        if not leg: continue
        if coords and coords[-1] == leg[0]:
            coords.extend(leg[1:])
        else:
            coords.extend(leg)
    return coords

feats = []
for s in services:
    coords = service_coords(s["rotation"])
    if len(coords) < 2: continue
    geom = {"type":"LineString","coordinates":unwrap(coords)}
    feats.append({"type":"Feature","id":s["id"],"geometry":geom,"properties":{
        "svc_id": s["id"], "name": s["name"], "lane": s["lane"], "teu": s["teu"],
        "terminal": TERM.get(s["terminal"], s["terminal"]), "term_code": s["terminal"],
        "n_calls": len(s["rotation"]),
        "rotation": " → ".join(ports[k]["name"] for k in s["rotation"])}})
json.dump({"type":"FeatureCollection","features":feats},
          open(WEB/"routes.geojson","w",encoding="utf-8"), ensure_ascii=False)

used = {}
for s in services:
    for k in s["rotation"]:
        used[k] = used.get(k, 0) + 1
pfeats = []
for k, cnt in used.items():
    p = ports[k]
    pfeats.append({"type":"Feature","geometry":{"type":"Point","coordinates":[p["lon"],p["lat"]]},
        "properties":{"key":k,"name":p["name"],"n_service":cnt,"is_houston": k=="houston"}})
json.dump({"type":"FeatureCollection","features":pfeats},
          open(WEB/"ports.geojson","w",encoding="utf-8"), ensure_ascii=False)

print(f"wrote web/data: {len(feats)} service routes, {len(pfeats)} ports")
