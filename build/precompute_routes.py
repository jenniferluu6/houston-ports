#!/usr/bin/env python3
"""Precompute genuine sea-lane geometry for every service leg using the searoute
marine network (routes follow shipping lanes through canals; they stay on water).
Output: data/searoutes.json  ->  { "fromKey>toKey": [[lon,lat],...], ... }
Longitudes are normalized to [-180,180]; the map splits polylines at the antimeridian."""
import json, pathlib, math, sys
import searoute as sr

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

def load(p):
    with open(p, encoding="utf-8") as f: return json.load(f)

ports = load(DATA / "ports.json")["ports"]
services = load(DATA / "services.json")["services"]

def norm(lon):  # wrap to [-180,180]
    return ((lon + 180) % 360) - 180

def gckm(o, d):
    R = 6371; la1, lo1, la2, lo2 = map(math.radians, [o[1], o[0], d[1], d[0]])
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))

cache = {}
anomalies = []

def route(a_key, b_key):
    key = f"{a_key}>{b_key}"
    if key in cache: return cache[key]
    a, b = ports[a_key], ports[b_key]
    o, d = [a["lon"], a["lat"]], [b["lon"], b["lat"]]
    try:
        r = sr.searoute(o, d, append_orig_dest=True)
        coords = r.geometry["coordinates"]
        L = r.properties.get("length", 0)
    except Exception as e:
        anomalies.append(f"{key}: FAIL {e} -> straight fallback")
        cache[key] = [[a["lon"], a["lat"]], [b["lon"], b["lat"]]]
        return cache[key]
    if len(coords) < 2:  # degenerate (adjacent nodes): straight segment
        coords = [o, d]
    gc = max(gckm(o, d), 1)
    if L / gc > 3.5:
        anomalies.append(f"{key}: detour ratio {L/gc:.1f} (len={L:.0f} gc={gc:.0f})")
    out = [[round(norm(p[0]), 3), round(p[1], 3)] for p in coords]
    cache[key] = out
    return out

needed = set()
for s in services:
    rot = s["rotation"]
    for i in range(len(rot)-1):
        if rot[i] != rot[i+1]:
            needed.add((rot[i], rot[i+1]))

result = {}
for a, b in sorted(needed):
    result[f"{a}>{b}"] = route(a, b)

with open(DATA / "searoutes.json", "w", encoding="utf-8") as f:
    json.dump(result, f, separators=(",", ":"))

print(f"legs computed: {len(result)}")
print("anomalies:", len(anomalies))
for x in anomalies: print("  -", x)
tot = sum(len(v) for v in result.values())
print(f"total vertices: {tot} (~{tot*12//1024} KB raw)")
