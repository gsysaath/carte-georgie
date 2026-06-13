#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Télécharge le fond de carte (rivières, plans d'eau, littoral, parcs, axes
principaux) de chaque ville depuis OpenStreetMap (API Overpass) et génère
citymap-data.js, lu par index.html pour dessiner les cartes de ville « façon
croquis », comme la carte nationale.

    python3 download_citymaps.py

Aucune dépendance : uniquement la bibliothèque standard de Python 3.
Données © contributeurs OpenStreetMap (ODbL).
"""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "citymap-data.js")
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
UA = "GeorgieTripMap/1.0 (carte de voyage perso, usage non commercial)"
RDP_TOL = 0.00022          # tolérance de simplification (~22 m)

# bbox (sud, ouest, nord, est) autour des points de chaque ville
VILLES = {
    "tbilissi": (41.66, 44.74, 41.74, 44.84),
    "mtskheta": (41.81, 44.68, 41.87, 44.75),
    "ananuri":  (42.10, 44.66, 42.20, 44.74),
    "kazbegi":  (42.61, 44.58, 42.70, 44.70),
    "borjomi":  (41.80, 43.33, 41.88, 43.45),
    "kutaisi":  (42.22, 42.65, 42.32, 42.75),
    "batumi":   (41.59, 41.58, 41.70, 41.68),
}


def overpass_query(s, w, n, e):
    b = "%f,%f,%f,%f" % (s, w, n, e)
    return (
        "[out:json][timeout:90];(" +
        'way["waterway"~"^(river|canal)$"](%s);' % b +
        'way["natural"="water"](%s);' % b +
        'relation["natural"="water"](%s);' % b +
        'way["natural"="coastline"](%s);' % b +
        'way["leisure"="park"](%s);' % b +
        'way["landuse"~"^(forest|grass|meadow|recreation_ground|cemetery)$"](%s);' % b +
        'way["highway"~"^(motorway|trunk|primary|secondary)$"](%s);' % b +
        ");out geom;"
    )


def fetch(query):
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    last = None
    for ep in ENDPOINTS:
        delay = 3.0
        for attempt in range(4):
            try:
                req = urllib.request.Request(ep, data=data, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=120) as r:
                    return json.loads(r.read().decode("utf-8"))
            except urllib.error.HTTPError as ex:
                last = ex
                if ex.code in (429, 504, 503) and attempt < 3:
                    print("    … HTTP %d — nouvelle tentative dans %.0fs" % (ex.code, delay))
                    time.sleep(delay); delay = min(delay * 2, 40); continue
                break
            except Exception as ex:
                last = ex; time.sleep(delay); delay = min(delay * 2, 40)
        print("    ! endpoint %s KO (%s) — essai suivant" % (ep.split("/")[2], last))
    raise RuntimeError("Overpass injoignable : %s" % last)


def rdp(pts, tol):
    """Douglas-Peucker en coordonnées (lat,lng)."""
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[1] - a[1], b[0] - a[0]
    nrm = (dx * dx + dy * dy) ** 0.5 or 1e-9
    dmax, idx = 0.0, 0
    for i in range(1, len(pts) - 1):
        p = pts[i]
        d = abs((p[1] - a[1]) * dy - (p[0] - a[0]) * dx) / nrm
        if d > dmax:
            dmax, idx = d, i
    if dmax > tol:
        left = rdp(pts[:idx + 1], tol)
        right = rdp(pts[idx:], tol)
        return left[:-1] + right
    return [a, b]


def geom_to_line(geom):
    pts = [[round(g["lat"], 5), round(g["lon"], 5)] for g in geom if "lat" in g and "lon" in g]
    if len(pts) >= 2:
        return rdp(pts, RDP_TOL)
    return None


def classify(el, layers):
    tags = el.get("tags", {})
    geoms = []
    if el["type"] == "way" and "geometry" in el:
        geoms = [el["geometry"]]
    elif el["type"] == "relation":
        geoms = [m["geometry"] for m in el.get("members", [])
                 if m.get("type") == "way" and m.get("role") in ("outer", "") and m.get("geometry")]
    for g in geoms:
        line = geom_to_line(g)
        if not line:
            continue
        if tags.get("natural") == "coastline":
            layers["coast"].append(line)
        elif tags.get("natural") == "water" or tags.get("waterway") in ("river", "canal"):
            (layers["rivers"] if tags.get("waterway") else layers["water"]).append(line)
        elif tags.get("leisure") == "park" or tags.get("landuse"):
            layers["green"].append(line)
        elif tags.get("highway"):
            layers["roads"].append(line)


def main():
    out = {}
    print("Fond de carte OpenStreetMap (Overpass)…\n")
    for key, (s, w, n, e) in VILLES.items():
        print("• %s" % key)
        try:
            data = fetch(overpass_query(s, w, n, e))
        except Exception as ex:
            print("    ! %s — ville ignorée" % ex)
            out[key] = {}
            continue
        layers = {"rivers": [], "water": [], "coast": [], "green": [], "roads": []}
        for el in data.get("elements", []):
            classify(el, layers)
        layers = {k: v for k, v in layers.items() if v}
        counts = " · ".join("%s:%d" % (k, len(v)) for k, v in layers.items()) or "rien"
        print("    %s" % counts)
        out[key] = layers
        time.sleep(2.0)

    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write("/* Fond de carte des villes — © contributeurs OpenStreetMap (ODbL). */\n")
        fh.write("/* Généré par download_citymaps.py. Coordonnées [lat, lng]. */\n")
        fh.write("window.CITYMAPS = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
    kb = os.path.getsize(SORTIE) / 1024
    print("\nÉcrit : %s (%.0f Ko)" % (os.path.relpath(SORTIE, ICI), kb))


if __name__ == "__main__":
    main()
