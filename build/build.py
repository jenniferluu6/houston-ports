#!/usr/bin/env python3
"""Assemble the standalone Houston container-routes map.
Reproducible: reads curated data + basemap + template, writes one self-contained HTML file.
Standard library only (no third-party deps)."""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "houston_container_routes.html"

def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    ports = load(DATA / "ports.json")
    services = load(DATA / "services.json")
    geo = load(DATA / "ne_110m_land.geojson")
    searoutes = load(DATA / "searoutes.json")

    # Trim the basemap to geometry only (drop bulky properties) to keep the file lean.
    geo_min = {"features": [
        {"geometry": ft["geometry"]} for ft in geo["features"]
        if ft.get("geometry")
    ]}

    tpl = (ROOT / "build" / "template.html").read_text(encoding="utf-8")
    html = (tpl
            .replace("__PORTS_JSON__", json.dumps(ports, separators=(",", ":")))
            .replace("__SERVICES_JSON__", json.dumps(services, separators=(",", ":")))
            .replace("__GEO_JSON__", json.dumps(geo_min, separators=(",", ":")))
            .replace("__SEAROUTES_JSON__", json.dumps(searoutes, separators=(",", ":"))))

    # Guard: no placeholder should survive.
    for marker in ("__PORTS_JSON__", "__SERVICES_JSON__", "__GEO_JSON__", "__SEAROUTES_JSON__"):
        if marker in html:
            print("ERROR: placeholder not replaced:", marker); sys.exit(1)

    OUT.write_text(html, encoding="utf-8")
    print("wrote", OUT, f"({len(html)//1024} KB)")
    print("services:", len(services["services"]),
          "| ports:", len(ports["ports"]),
          "| land features:", len(geo_min["features"]))

if __name__ == "__main__":
    main()
