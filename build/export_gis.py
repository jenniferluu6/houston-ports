#!/usr/bin/env python3
"""Export Port Houston container routes for ArcGIS.
Writes WGS84 (EPSG:4326) polyline + point shapefiles (and matching GeoJSON) into gis_export/:
  - port_houston_routes_by_service : one polyline per liner service (full rotation)
  - port_houston_routes_by_leg     : one polyline per port-to-port leg
  - port_houston_ports             : one point per port
Lines are split at the antimeridian into multipart geometry so nothing slashes across the map.
Dependencies: pyshp (pure Python). No GDAL required."""
import json, pathlib, shapefile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "gis_export"; OUT.mkdir(exist_ok=True)

ports    = json.load(open(DATA/"ports.json", encoding="utf-8"))["ports"]
db       = json.load(open(DATA/"services.json", encoding="utf-8"))
services = db["services"]
routes   = json.load(open(DATA/"searoutes.json", encoding="utf-8"))
TERM = {"BPT": "Bayport", "BCT": "Barbours Cut"}

# Esri WKT for WGS84 geographic
PRJ = ('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,'
       '298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]')

def split_am(coords):
    """Split a lon/lat polyline into parts wherever it crosses the antimeridian."""
    parts, cur = [], [coords[0]]
    for i in range(1, len(coords)):
        if abs(coords[i][0] - coords[i-1][0]) > 180:
            parts.append(cur); cur = [coords[i]]
        else:
            cur.append(coords[i])
    parts.append(cur)
    return [p for p in parts if len(p) > 1]

def service_coords(rot):
    """Concatenate a service's legs in rotation order (dedup shared endpoints)."""
    coords = []
    for i in range(len(rot)-1):
        if rot[i] == rot[i+1]:
            continue
        leg = routes.get(rot[i]+">"+rot[i+1])
        if not leg:
            continue
        if coords and coords[-1] == leg[0]:
            coords.extend(leg[1:])
        else:
            coords.extend(leg)
    return coords

def write_prj(path):
    with open(str(path)+".prj", "w", encoding="utf-8") as f:
        f.write(PRJ)

# ---- 1) routes by service ----
p = OUT/"port_houston_routes_by_service"
w = shapefile.Writer(str(p), shapeType=shapefile.POLYLINE)
w.field("SVC_ID","C",25); w.field("NAME","C",60); w.field("LANE","C",20)
w.field("TEU","N",8); w.field("TERMINAL","C",16); w.field("TERM_CODE","C",4); w.field("N_CALLS","N",4)
for s in services:
    parts = split_am(service_coords(s["rotation"]))
    if not parts: continue
    w.line(parts)
    w.record(s["id"], s["name"], s["lane"], s["teu"],
             TERM.get(s["terminal"], s["terminal"]), s["terminal"], len(s["rotation"]))
w.close(); write_prj(p)
n_svc = len(services)

# ---- 2) routes by leg ----
p = OUT/"port_houston_routes_by_leg"
w = shapefile.Writer(str(p), shapeType=shapefile.POLYLINE)
w.field("SVC_ID","C",25); w.field("LANE","C",20); w.field("SEQ","N",4)
w.field("FROM_PORT","C",40); w.field("TO_PORT","C",40); w.field("TEU","N",8); w.field("TERM_CODE","C",4)
n_leg = 0
for s in services:
    rot = s["rotation"]
    for i in range(len(rot)-1):
        if rot[i] == rot[i+1]: continue
        leg = routes.get(rot[i]+">"+rot[i+1])
        if not leg: continue
        parts = split_am(leg)
        if not parts: continue
        w.line(parts)
        w.record(s["id"], s["lane"], i+1, ports[rot[i]]["name"], ports[rot[i+1]]["name"],
                 s["teu"], s["terminal"])
        n_leg += 1
w.close(); write_prj(p)

# ---- 3) ports ----
used = {}
for s in services:
    for k in s["rotation"]:
        used[k] = used.get(k, 0) + 1
p = OUT/"port_houston_ports"
w = shapefile.Writer(str(p), shapeType=shapefile.POINT)
w.field("PORT_KEY","C",20); w.field("NAME","C",60); w.field("LAT","N",12,6); w.field("LON","N",12,6)
w.field("N_SERVICE","N",4); w.field("FLAG","C",254)
for k, cnt in sorted(used.items()):
    pt = ports[k]
    w.point(pt["lon"], pt["lat"])
    w.record(k, pt["name"], pt["lat"], pt["lon"], cnt, pt.get("flag","")[:254])
w.close(); write_prj(p)
n_port = len(used)

# ---- GeoJSON twins (ArcGIS Pro reads these natively; no shapefile field/2GB limits) ----
def line_feature(coords, props):
    parts = split_am(coords)
    geom = ({"type":"LineString","coordinates":parts[0]} if len(parts)==1
            else {"type":"MultiLineString","coordinates":parts})
    return {"type":"Feature","properties":props,"geometry":geom}

fc_svc = {"type":"FeatureCollection","features":[
    line_feature(service_coords(s["rotation"]),
        {"svc_id":s["id"],"name":s["name"],"lane":s["lane"],"teu":s["teu"],
         "terminal":TERM.get(s["terminal"],s["terminal"]),"n_calls":len(s["rotation"]),
         "rotation":" > ".join(ports[k]["name"] for k in s["rotation"])})
    for s in services if service_coords(s["rotation"])]}
json.dump(fc_svc, open(OUT/"port_houston_routes_by_service.geojson","w",encoding="utf-8"))

fc_leg = {"type":"FeatureCollection","features":[]}
for s in services:
    rot=s["rotation"]
    for i in range(len(rot)-1):
        if rot[i]==rot[i+1]: continue
        leg=routes.get(rot[i]+">"+rot[i+1])
        if not leg: continue
        fc_leg["features"].append(line_feature(leg,
            {"svc_id":s["id"],"lane":s["lane"],"seq":i+1,
             "from_port":ports[rot[i]]["name"],"to_port":ports[rot[i+1]]["name"],
             "teu":s["teu"],"term_code":s["terminal"]}))
json.dump(fc_leg, open(OUT/"port_houston_routes_by_leg.geojson","w",encoding="utf-8"))

print(f"OK  services={n_svc}  legs={n_leg}  ports={n_port}")
print("wrote to", OUT)
